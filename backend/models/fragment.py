#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Self

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from backend.enums.review_state import ReviewState
from backend.enums.transformer_status import TransformerStatus
from backend.transformer.result import ProcessorResult
from backend.size_calculator.base import SizeCalculatorBase
from backend.size_calculator.manager import size_calculator_manager
from .content_user import ContentUser
from .document import Document


class Fragment(ContentUser):
    """
    A fragment of a document.
    """

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="fragments")
    """The document that is owning this fragment."""

    position = models.IntegerField()
    """The position (index) in the document."""

    first_line_number = models.PositiveIntegerField(null=True)
    """The first line number of the fragment from the original document."""

    size = models.BigIntegerField()
    """The size that was used to split the document into fragment. The unit is stored in the document."""

    size_bytes = models.BigIntegerField()
    """Standard size for convenience: Bytes for UTF-8 encoding."""

    size_characters = models.BigIntegerField()
    """Standard size for convenience: Characters"""

    size_words = models.BigIntegerField()
    """Standard size for convenience: Words (white space separated)"""

    size_lines = models.BigIntegerField()
    """Standard size for convenience: Lines (newline separated)"""

    review_state = models.SmallIntegerField(choices=ReviewState.choices, default=ReviewState.UNPROCESSED.value)
    """The review state for this fragment."""

    has_text_changes = models.BooleanField(default=False)
    """If this fragment has text changes in its current state."""

    context = models.JSONField(null=True)
    """Context information for this fragment."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the fragment was created."""

    modified = models.DateTimeField(auto_now=True)
    """The date when the fragment was last modified."""

    @property
    def review_state_identifier(self) -> str:
        """Get the review state as lower-case identifier."""
        return ReviewState(self.review_state).name.lower()

    @property
    def review_state_label(self) -> str:
        """Get the UI label for the review state."""
        return str(ReviewState(self.review_state).label)

    @property
    def has_edit(self) -> bool:
        """Test if this fragment has an edit."""
        try:
            if self.edit:
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    @property
    def edit_text(self) -> str:
        """
        Get the text of the edit, or an empty text if there is no edit.
        """
        try:
            return self.edit.text
        except ObjectDoesNotExist:
            return ""

    @property
    def has_transformation(self) -> bool:
        """Test if this fragment has a transformation."""
        try:
            if self.transformation:
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    @property
    def has_edit_and_transformation(self) -> bool:
        return self.has_edit and self.has_transformation

    @property
    def has_failed_transformation(self) -> bool:
        try:
            return self.transformation.status == TransformerStatus.FAILURE
        except ObjectDoesNotExist:
            return False

    @property
    def transformation_text(self) -> str:
        """
        Get the text of the transformation, or an empty text if there is no transformation.
        """
        try:
            return self.transformation.text
        except ObjectDoesNotExist:
            return ""

    @property
    def transformation_output(self) -> str:
        """
        Get the output of the transformation, or an empty text if there is no transformation.
        """
        try:
            return self.transformation.output
        except ObjectDoesNotExist:
            return ""

    @property
    def final_text(self) -> str:
        """
        Get the final text. The final text is an edit, if one exists, or the processed text if it exists or
        of none of these exist, the source text.
        """
        try:
            return self.edit.text
        except ObjectDoesNotExist:
            pass
        try:
            return self.transformation.text
        except ObjectDoesNotExist:
            pass
        return self.text

    @property
    def is_unprocessed(self) -> bool:
        """
        if this fragment is in approved state.
        """
        return self.review_state == ReviewState.UNPROCESSED

    @property
    def is_rejected(self) -> bool:
        """
        if this fragment is in approved state.
        """
        return self.review_state == ReviewState.REJECTED

    @property
    def is_approved(self) -> bool:
        """
        If this fragment in approved state.
        """
        return self.review_state == ReviewState.APPROVED

    @property
    def is_pending(self) -> bool:
        """
        If this fragment in pending state.
        """
        return self.review_state == ReviewState.PENDING

    def _update_text_changes(self) -> None:
        """
        Update the `has_text_changes` field.
        """
        has_edit = self.has_edit
        has_transformation = self.has_transformation
        if has_edit:
            self.has_text_changes = self.edit.text != self.text
            return
        if has_transformation:
            self.has_text_changes = self.transformation.text != self.text
            return
        self.has_text_changes = False

    def delete_edit(self) -> None:
        """
        Delete an existing edit from the fragment.
        Resets the status to 'pending'.
        """
        try:
            self.edit.delete()
            self._update_text_changes()
            if self.has_text_changes:
                self.review_state = ReviewState.PENDING
            else:
                self.review_state = ReviewState.UNPROCESSED
        except ObjectDoesNotExist:
            pass

    def delete_transformation(self) -> None:
        """
        Delete an existing transformation from the fragment.
        Resets the status to 'pending'
        """
        try:
            self.transformation.delete()
            self._update_text_changes()
            if self.has_text_changes:
                self.review_state = ReviewState.PENDING
            else:
                self.review_state = ReviewState.UNPROCESSED
        except ObjectDoesNotExist:
            pass

    def set_edit_text(self, text: str, notes: str = "") -> None:
        """
        Set or update the text of a manual edit.

        :param text: The text.
        :param notes: Notes to add.
        """
        from backend.models.fragment_edit import FragmentEdit

        if not self.has_edit:
            self.edit = FragmentEdit.objects.create(fragment=self, notes=notes)
        else:
            self.edit.notes = notes
        existing_content = [self.content]
        if self.has_transformation:
            existing_content.append(self.transformation.content)
        self.edit.set_text(text, existing_content)
        self.edit.save()
        self._update_text_changes()
        self.save()

    def set_transformation(
        self, transformation: "Transformation", transformation_result: ProcessorResult, auto_approve_unchanged: bool
    ) -> bool:
        """
        Set or overwrite the transformation of this fragment.

        - Existing edits are removed from this fragment.
        - Existing transformations are removed from this fragment.
        - The status is reset to 'pending'.

        :param transformation: The transformation that modifies this fragment.
        :param transformation_result: The transformation result to use.
        :param auto_approve_unchanged: If unchanged content shall be marked as approved.
        :return: `True` if the transformation did change the text of this fragment.
        """
        from .fragment_transformation import FragmentTransformation

        self.delete_edit()
        self.delete_transformation()

        self.review_state = ReviewState.PENDING
        self.transformation = FragmentTransformation.objects.create(
            fragment=self,
            status=transformation_result.status,
            output=transformation_result.output,
            failure_input=transformation_result.failure_input,
            failure_reason=transformation_result.failure_reason,
            transformation=transformation,
        )
        self.transformation.set_text(transformation_result.content, [self.content])
        self._update_text_changes()
        if auto_approve_unchanged and not self.has_text_changes:
            self.review_state = ReviewState.APPROVED
        self.save()
        return self.has_text_changes

    def create_copy_for_revision(
        self, *, document: Document, size_calculator: SizeCalculatorBase, first_line_number: int, copy_review: bool
    ) -> Self:
        """
        Create a copy of this fragment for new revisions.

        Copies the `final_text` of this fragment into a new one. Also calculates the sizes for the
        new fragment.

        :param document: The document to add this fragment to.
        :param size_calculator: The size calculator to use for the `size` attribute.
        :param first_line_number: The first line number of this fragment.
        :param copy_review: Whether the review state from this fragment shall be copied.
        """
        review_state = ReviewState.UNPROCESSED
        if copy_review:
            review_state = self.review_state
        text = self.final_text
        size = size_calculator.size_for_text(text)
        default_sizes = size_calculator_manager.default_sizes_for_text(text)
        size_bytes = default_sizes.bytes_utf8
        size_characters = default_sizes.characters
        size_words = default_sizes.words
        size_lines = default_sizes.lines
        new_fragment = Fragment.objects.create(
            document=document,
            position=self.position,
            first_line_number=first_line_number,
            size=size,
            size_bytes=size_bytes,
            size_characters=size_characters,
            size_words=size_words,
            size_lines=size_lines,
            review_state=review_state,
            context=self.context,
        )
        if self.has_edit:
            existing_content = [self.edit.content]
        elif self.has_transformation:
            existing_content = [self.transformation.content]
        else:
            existing_content = None
        new_fragment.set_text(self.final_text, existing_content)
        new_fragment.save()
        return new_fragment

    def __str__(self):
        return (
            f"{self.position} in document {self.document.name}, transformation={self.has_transformation}, "
            f"edit={self.has_edit}, has_text_changes={self.has_text_changes}"
        )

    class Meta:
        verbose_name = "Document Fragment"
        verbose_name_plural = "Document Fragments"
        indexes = [models.Index(fields=["document", "position"], name="fragment_idx_main")]
        constraints = [models.UniqueConstraint(fields=["document", "position"], name="fragment_unique_main")]
