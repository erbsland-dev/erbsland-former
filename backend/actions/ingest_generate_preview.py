#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from pathlib import Path
from typing import Optional

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from backend.actions.ingest_base import IngestBase
from backend.enums.ingest_planed_action import IngestPlanedAction
from backend.enums.ingest_step import IngestStep
from backend.models.content import Content
from backend.models.document import Document
from backend.models.fragment import Fragment
from backend.models.ingest_document import IngestDocument
from backend.size_calculator.manager import size_calculator_manager
from backend.splitter.block import SplitterBlock
from backend.splitter.line_reader import FileLineReader
from backend.splitter.splitter import Splitter
from backend.splitter.stats import SplitterStats
from backend.syntax_handler import syntax_manager
from tasks.actions import ActionError


class IngestGeneratePreview(IngestBase):
    name = "ingest_generate_preview"
    progress_title = _("Generating Preview")
    progress_subject = _("Preview")

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)
        self.ingest_document: Optional[IngestDocument] = None
        self.document_count: int = 0
        self.document_index: int = 0
        self.splitter_stats = SplitterStats()
        self.document: Optional[Document] = None

    def run(self, input_data: dict) -> None:
        self.log_info(_("Start generating the ingest preview."))
        try:
            with transaction.atomic():
                self.set_db_object_from_input_data(input_data)
                if self.ingest_assistant.step != IngestStep.PREPARING_PREVIEW:
                    raise ActionError(_("The ingest operation is in the wrong state."))
                self.working_directory = Path(self.ingest_assistant.working_directory)
                ingest_documents = self.ingest_assistant.documents.filter(planed_action=IngestPlanedAction.ADD)
                self.document_count = ingest_documents.count()
                for index, ingest_document in enumerate(ingest_documents):
                    self.document_index = index
                    self.ingest_document = ingest_document
                    self.process_document()

                self.ingest_assistant.step = IngestStep.PREVIEW
                self.ingest_assistant.statistics = {
                    "documents": self.document_count,
                    "fragments": self.splitter_stats.fragment_count,
                    "units": self.splitter_stats.unit_count,
                    "bytes": self.splitter_stats.byte_count,
                    "characters": self.splitter_stats.character_count,
                    "words": self.splitter_stats.word_count,
                    "lines": self.splitter_stats.line_count,
                }
                self.ingest_assistant.save()
            self.log_info(_("Successfully generated the ingest preview."))
        except Exception as error:
            # In case of any error, go back to the setup step.
            self.log_error(_("Failed to generate the ingest preview, rolling back."))
            with transaction.atomic():
                self.ingest_assistant.step = IngestStep.SETUP
                self.ingest_assistant.save()
            raise

    def log_per_document_message(self, message: str):
        """
        Log a document message and prefix it with the document index and count.

        :param message: The message to log.
        """
        values = {
            "index": self.document_index,
            "count": self.document_count,
            "message": message,
        }
        message = _("Document %(index)d/%(count)d: %(message)s") % values
        self.log_info(message)
        self.set_progress(float(self.document_index), float(self.document_count), message)

    @staticmethod
    def detect_line_endings(path: Path) -> str:
        """
        Detect the line ending for a document.

        If detection is possible, either "lf" or "crlf". If detection isn't possible, "lf" is returned.
        """
        try:
            with open(path, "rt", encoding="utf-8", newline=None) as file:
                lf_count = 0
                crlf_count = 0
                for _ in range(10):
                    line = file.readline(100_000)
                    if not line:
                        break
                    if "\r\n" in line:
                        lf_count += 1
                    elif "\n" in line:
                        crlf_count += 1
            if lf_count > 0 and crlf_count > 0:
                if lf_count > crlf_count:
                    return "lf"
                return "crlf"
        except UnicodeEncodeError:
            pass
        return "lf"

    def process_document(self):
        """
        Process a single document.
        """
        self.log_per_document_message(_("Preparing environment"))
        folder = self.ingest_document.folder.strip("/ ")
        if folder:
            path = folder + "/" + self.ingest_document.name
        else:
            path = self.ingest_document.name
        local_path = self.working_directory / self.ingest_document.local_path
        line_endings = self.detect_line_endings(local_path)
        self.document = Document.objects.create(
            revision=self.revision,
            path=path,
            encoding="utf-8",
            line_endings=line_endings,
            is_preview=True,
            document_syntax=self.ingest_document.document_syntax,
            minimum_fragment_size=self.ingest_assistant.minimum_fragment_size,
            maximum_fragment_size=self.ingest_assistant.maximum_fragment_size,
            size_unit=self.ingest_assistant.size_unit,
        )
        self.log_per_document_message(_("Analyzing and splitting into blocks."))
        self.document.import_from_file(local_path, self.splitter_stats)
        self.log_per_document_message(_("Done"))
