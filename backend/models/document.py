#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property
from pathlib import Path
from typing import Self

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from backend.enums import ReviewStateCounts, ReviewState, TransformerStatus
from backend.enums.line_endings import LineEndings
from backend.enums.transformation_state import TransformationStateCounts, TransformationState
from backend.size_calculator.manager import size_calculator_manager
from backend.splitter.block import SplitterBlock
from backend.splitter.line_reader import FileLineReader
from backend.splitter.splitter import Splitter
from backend.splitter.stats import SplitterStats
from backend.syntax_handler import syntax_manager
from backend.tools.definitions import IDENTIFIER_LENGTH, PATH_LENGTH
from backend.tools.validators import identifier_validator, path_validator


class Document(models.Model):
    """
    A folder or document in a project.
    """

    MAX_SHORTENED_LENGTH = 30

    revision = models.ForeignKey("Revision", on_delete=models.CASCADE, related_name="documents")
    """The revision of the node."""

    path = models.CharField(max_length=PATH_LENGTH, validators=[path_validator])
    """The full path of this document, including 'name' as last element."""

    encoding = models.CharField(max_length=16, default="utf-8")
    """The encoding of the source file of this document."""

    line_endings = models.CharField(max_length=4, default="lf", choices=LineEndings)
    """The line ending format for this document. Valid values are "lf" or "crlf"."""

    is_preview = models.BooleanField(default=False)
    """If this node is part of a preview while an ingest operation is running."""

    predecessor = models.ForeignKey("Document", null=True, related_name="successors", on_delete=models.SET_NULL)
    """The successors of this document node."""

    document_syntax = models.CharField(null=True, max_length=IDENTIFIER_LENGTH, validators=[identifier_validator])
    """The syntax of this document. Copy from import."""

    minimum_fragment_size = models.PositiveBigIntegerField(null=True)
    """The minimum size of a text fragment. Copy from import."""

    maximum_fragment_size = models.PositiveBigIntegerField(null=True)
    """The maximum size of a text fragment. Copy from import."""

    size_unit = models.CharField(null=True, max_length=IDENTIFIER_LENGTH, validators=[identifier_validator])
    """The unit that is used for the size calculation. Copy from import."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the node was created."""

    modified = models.DateTimeField(auto_now=True)
    """The date when the node was last modified."""

    @cached_property
    def path_parts(self) -> list[str]:
        """
        Get the individual parts of the path.
        """
        return self.path.strip("/").split("/")

    @cached_property
    def name(self) -> str:
        """
        Get the name of this document.
        """
        return self.path_parts[-1]

    @cached_property
    def folder(self) -> str:
        """
        Get the folder of this document, if any.
        """
        return "/".join(self.path_parts[:-1])

    @cached_property
    def level(self) -> int:
        """
        Get the level of this document node.
        """
        return self.path.count("/")

    @cached_property
    def document_syntax_verbose_name(self) -> str:
        """
        The document syntax for display in the UI.
        """
        return syntax_manager.verbose_name(self.document_syntax)

    @property
    def fragment_count(self) -> int:
        return self.fragments.count()

    @staticmethod
    def _elide_text(text: str, max_length: int, elide_str: str = "…") -> str:
        if len(text) <= max_length:
            return text
        half_max = (max_length - len(elide_str)) // 2
        return f"{text[:half_max]}{elide_str}{text[-half_max:]}"

    def get_shortened_name(self) -> str:
        return self._elide_text(self.name, self.MAX_SHORTENED_LENGTH)

    def get_shortened_path(self) -> str:
        result = self.path
        parts = self.path.strip("/").split("/")
        if len(parts) > 3:
            # Only keep the first directory, the last directory, and the filename
            result = "/".join([parts[0], "…", parts[-2], parts[-1]])
        if len(result) <= self.MAX_SHORTENED_LENGTH:
            return result
        return self._elide_text(self.path, self.MAX_SHORTENED_LENGTH)

    def review_states(self) -> ReviewStateCounts:
        """
        Get the number of review states for the document fragments.
        """
        states = self.fragments.values("review_state").annotate(total=models.Count("id"))
        result: dict[ReviewState, int] = {}
        for state in states:
            result[ReviewState(state["review_state"])] = state["total"]
        return ReviewStateCounts.from_dict(result)

    @classmethod
    def transformation_states_from_documents(cls, documents: QuerySet[Self]) -> TransformationStateCounts:
        """
        Get transformation states from a list of documents.

        :param documents: The documents to analyze.
        :return: The transformation state counts.
        """
        count_source = models.Count(
            "fragments", filter=models.Q(fragments__transformation__isnull=True, fragments__edit__isnull=True)
        )
        count_success = models.Count(
            "fragments",
            filter=models.Q(
                fragments__transformation__isnull=False,
                fragments__edit__isnull=True,
                fragments__transformation__status=TransformerStatus.SUCCESS.value,
            ),
        )
        count_failed = models.Count(
            "fragments",
            filter=models.Q(
                fragments__transformation__isnull=False,
                fragments__edit__isnull=True,
                fragments__transformation__status=TransformerStatus.FAILURE.value,
            ),
        )
        count_edited = models.Count("fragments", filter=models.Q(fragments__edit__isnull=False))
        counts = (
            documents.annotate(
                source=count_source,
                success=count_success,
                failed=count_failed,
                edited=count_edited,
            )
            .values("source", "success", "failed", "edited")
            .aggregate(
                source_sum=models.Sum("source"),
                success_sum=models.Sum("success"),
                failed_sum=models.Sum("failed"),
                edited_sum=models.Sum("edited"),
            )
        )
        result: dict[TransformationState, int] = {
            TransformationState.SOURCE: counts["source_sum"],
            TransformationState.SUCCESS: counts["success_sum"],
            TransformationState.FAILED: counts["failed_sum"],
            TransformationState.EDITED: counts["edited_sum"],
        }
        return TransformationStateCounts.from_dict(result)

    def transformation_states(self) -> TransformationStateCounts:
        """
        Get the transformation states for all document fragments.
        """
        return self.transformation_states_from_documents(Document.objects.filter(id=self.id))

    @property
    def has_text_changes(self) -> bool:
        """
        If one of the fragments in this document has transformations or edits.
        """
        return any(fragment.has_text_changes for fragment in self.fragments.all())

    def create_copy_for_revision(self, revision: "Revision") -> Self:
        """
        Create a copy for a new revision of the document.

        Creates a copt of this document object, without the fragments, for a new revision. Does only copy the
        document with the following attributes: "path", "is_preview", "successors", "document_syntax", "minimum_fragment_size",

        :return:
        """
        new_document = Document.objects.create(
            revision=revision,
            path=self.path,
            encoding=self.encoding,
            is_preview=False,
            predecessor=self,
            document_syntax=self.document_syntax,
            minimum_fragment_size=self.minimum_fragment_size,
            maximum_fragment_size=self.maximum_fragment_size,
            size_unit=self.size_unit,
        )
        return new_document

    def import_from_file(self, path: Path, splitter_stats: SplitterStats = None) -> None:
        """
        Import fragments from a file, using the syntax/unit settings from this document.

        :param path: The path of the file.
        :param splitter_stats: Optional object to collect splitter statistics.
        """
        if not isinstance(path, Path):
            raise TypeError("'path' must be a Path object")
        if splitter_stats is not None and not isinstance(splitter_stats, SplitterStats):
            raise TypeError("'splitter_stats' must be a SplitterStats object")

        from backend.models.content import Content
        from backend.models.fragment import Fragment

        syntax_handler = syntax_manager.create_for_name(self.document_syntax)
        size_calculator = size_calculator_manager.get_extension(self.size_unit)
        with FileLineReader(path, encoding=self.encoding) as line_reader:
            splitter = Splitter(
                line_reader=line_reader,
                syntax=syntax_handler,
                size_calculator=size_calculator,
                minimum_size=self.minimum_fragment_size,
                maximum_size=self.maximum_fragment_size,
            )
            index: int
            block: SplitterBlock
            for index, block in enumerate(splitter):
                content = Content.objects.create(text=block.text)
                default_sizes = size_calculator_manager.default_sizes_for_text(block.text)
                Fragment.objects.create(
                    document=self,
                    position=index,
                    content=content,
                    size=block.size,
                    size_bytes=default_sizes.bytes_utf8,
                    size_characters=default_sizes.characters,
                    size_words=default_sizes.words,
                    size_lines=default_sizes.lines,
                    first_line_number=block.line_number,
                    context=block.context,
                )
                if splitter_stats is not None:
                    splitter_stats.unit_count += block.size
                    splitter_stats.byte_count += default_sizes.bytes_utf8
                    splitter_stats.character_count += default_sizes.characters
                    splitter_stats.word_count += default_sizes.words
                    splitter_stats.line_count += default_sizes.lines
                    splitter_stats.fragment_count += 1

    def export_to_file(self, path: Path) -> None:
        """
        Export the document back into a file.

        :param path: The path for the file.
        """
        with path.open("wt", encoding=self.encoding) as fp:
            for fragment in self.fragments.order_by("position"):
                text = fragment.final_text
                if self.line_endings == "crlf":
                    text = text.replace("\n", "\r\n")
                fp.write(text)

    def __str__(self):
        return f'path="{self.path}" revision={self.revision.number} {"is-preview" if self.is_preview else ""}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear the caches in case this instance is updated.
        for property_name in ["path_parts", "name", "folder", "level"]:
            if hasattr(self, property_name):
                delattr(self, property_name)

    @staticmethod
    def ordering_by_file_first(model_instance: "Document") -> (str, str):
        return model_instance.folder.lower(), model_instance.name.lower()

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        indexes = [
            models.Index(fields=["revision"], name="document_node_idx_main"),
            models.Index(fields=["path"], name="document_node_idx_path"),
        ]
        constraints = [models.UniqueConstraint(fields=["revision", "path"], name="document_node_unique_main")]
