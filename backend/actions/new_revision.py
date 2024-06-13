#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from backend.enums.new_revision_step import NewRevisionStep
from backend.models import Revision, Document, Fragment, Project, RevisionAssistant
from backend.size_calculator.base import SizeCalculatorBase
from backend.size_calculator.manager import size_calculator_manager
from tasks.actions import ActionBase, ActionError


class NewRevision(ActionBase):
    """
    The action to create a new revision.
    """

    name = "new_revision"
    progress_title = _("Creating a New Revision")
    progress_subject = _("Creation of New Revision")

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)
        self.revision_assistant: Optional[RevisionAssistant] = None
        self.temp_dir: Optional[Path] = None
        self.old_revision: Optional[Revision] = None
        self.project: Optional[Project] = None
        self.revision_label: str = ""
        self.keep_fragments: bool = False
        self.copy_review: bool = False
        self.new_revision: Optional[Revision] = None

    def run(self, input_data: dict) -> None:
        self.log_info(_("Creating a new revision."))
        self.create_temporary_directory()
        try:
            with transaction.atomic():
                self.initialize(input_data)
                self.create_new_revision_object()
                self.create_new_documents()
                self.revision_assistant.step = NewRevisionStep.DONE
                self.revision_assistant.save()
            self.set_progress(100.0, 100.0, _("Successfully created the new revision"))
            self.log_info(_("Successfully created the new revision."))
        except Exception:
            self.log_error(_("Failed to create the revision."))
            raise
        finally:
            self.cleanup()

    def create_temporary_directory(self):
        """
        Create a new temporary working directory.
        """
        working_dir = Path(settings.BACKEND_WORKING_DIR)
        self.temp_dir = working_dir / f"new_revision_{uuid.uuid4()}"
        try:
            self.temp_dir.mkdir(parents=True)
        except Exception as error:
            self.log_debug(f"Failed to create temporary directory. path={self.temp_dir} error={error}")
            raise ActionError(_("The working directory cannot be accessed."))

    def initialize(self, input_data: dict) -> None:
        self.set_progress(0.0, 100.0, _("Initializing"))
        self.revision_assistant = RevisionAssistant.objects.get(pk=input_data["revision_assistant_pk"])
        self.old_revision = self.revision_assistant.revision
        self.project = self.old_revision.project
        self.revision_label = self.revision_assistant.revision_label
        self.copy_review = self.revision_assistant.copy_review
        self.keep_fragments = self.revision_assistant.keep_fragments

    def create_new_revision_object(self) -> None:
        # The currently latest version is now a regular one.
        latest_revision = self.project.get_latest_revision()
        latest_revision.is_latest = False
        latest_revision.save()
        # Create the new revision
        self.new_revision = Revision(
            project=self.project,
            number=int(latest_revision.number) + 1,
            label=self.revision_label,
            is_latest=True,
            predecessor=self.old_revision,
        )
        self.new_revision.save()

    def create_new_documents(self) -> None:
        """
        Create the new documents for the revision, based on the old ones.
        """
        documents = self.old_revision.documents.order_by("path")
        document_count = documents.count()
        for index, document in enumerate(documents.all()):
            self.set_progress(
                float(index),
                float(document_count),
                _("Processing document: %(path)s") % {"path": document.get_shortened_path()},
            )
            if self.keep_fragments or not document.has_text_changes:
                self.copy_document_keeping_its_fragments(document)
            else:
                self.re_split_document(document)

    def copy_document_keeping_its_fragments(self, document: Document) -> None:
        """
        Clone a document and its fragments, keeping all splitting points and metadata.
        """
        new_document = document.create_copy_for_revision(self.new_revision)
        size_calculator: SizeCalculatorBase = size_calculator_manager.get_extension(document.size_unit)
        line_number = 1
        for fragment in document.fragments.order_by("position"):
            new_fragment = fragment.create_copy_for_revision(
                document=new_document,
                size_calculator=size_calculator,
                first_line_number=line_number,
                copy_review=self.copy_review,
            )
            line_number += new_fragment.size_lines

    def re_split_document(self, document: Document) -> None:
        """
        Re-split a document using the latest contents.
        """
        tmp_path = self.temp_dir / f"file_{uuid.uuid4()}.tmp"
        try:
            document.export_to_file(tmp_path)
        except IOError as error:
            self.log_debug(f"Failed export the document for splitting. path={tmp_path} error={error}")
            raise ActionError(_("Could not export document for splitting."))
        new_document = document.create_copy_for_revision(self.new_revision)
        try:
            new_document.import_from_file(tmp_path)
        except Exception as error:
            self.log_debug(f"Failed to import document for splitting. path={tmp_path} error={error}")
            raise ActionError(_("Could not import and split a document."))

    def cleanup(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None

    def on_stopped(self) -> None:
        self.cleanup()

    def on_failed(self, error: Exception) -> None:
        self.cleanup()
