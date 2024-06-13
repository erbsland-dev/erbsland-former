#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import logging
import zipfile
from pathlib import Path
from typing import Optional

from django.db import transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from backend.enums.egress_step import EgressStep
from backend.models import Revision
from backend.models.egress_assistant import EgressAssistant
from tasks.actions import ActionBase, ActionError


class EgressAction(ActionBase):
    """
    The actual action for the egress operation.
    """

    name = "egress"
    progress_title = _("Exporting Documents")
    progress_subject = _("Document Export")

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)
        self.egress_assistant: Optional[EgressAssistant] = None
        self.revision: Optional[Revision] = None
        self.working_dir: Optional[Path] = None
        self.zip_file: Optional[Path] = None

    def set_db_object_from_input_data(self, input_data: dict) -> None:
        """
        Set the assistant instance from the input data and verify it is valid.

        :param input_data: The input data.
        """
        if "egress_assistant_pk" not in input_data:
            raise ActionError(_("There was a problem with the input data."))
        egress_assistant_pk = input_data["egress_assistant_pk"]
        if not isinstance(egress_assistant_pk, str):
            raise ActionError(_("There was a problem with the input data."))
        try:
            self.egress_assistant = EgressAssistant.objects.get(pk=egress_assistant_pk)
            self.revision = self.egress_assistant.revision
        except EgressAssistant.DoesNotExist:
            raise ActionError(_("Could not find the data from the export assistant."))

    def create_working_dir(self) -> None:
        """
        Create the working directory for this assistant.
        """
        working_base_dir = Path(settings.BACKEND_WORKING_DIR)
        self.working_dir = working_base_dir / f"egress_{self.egress_assistant.pk}"
        if self.working_dir.exists():
            raise ActionError(_("The working directory for this export assistant already exists."))
        self.working_dir.mkdir(parents=True)
        self.egress_assistant.working_directory = self.working_dir
        self.egress_assistant.save()

    def build_zip_file(self) -> None:
        """
        Export all selected documents into a new ZIP file.
        """
        self.zip_file = self.working_dir / "export.zip"
        document_count = self.egress_assistant.documents.count()
        with zipfile.ZipFile(self.zip_file, mode="w") as zip_handle:
            for index, document in enumerate(self.egress_assistant.get_selected_documents()):
                self.set_progress(
                    float(index), float(document_count), _("Writing document: %(path)s") % {"path": document.path}
                )
                with zip_handle.open(document.path, mode="w", force_zip64=True) as fp:
                    for fragment in document.fragments.order_by("position"):
                        fp.write(fragment.final_text.encode(document.encoding))

    def run(self, input_data: dict) -> None:
        self.log_info(_("Start analyzing the upload."))
        # With the first atomic operation, create and save the working dir in the assistant.
        # This makes sure, that wenn the assistant object gets deleted, the working dir is deleted with the object.
        with transaction.atomic():
            self.set_db_object_from_input_data(input_data)
            if self.egress_assistant.step != EgressStep.RUNNING:
                raise ActionError(_("The egress operation is in the wrong state."))
            self.create_working_dir()
        # In the next atomic operation, create the export and switch the step to DONE.
        with transaction.atomic():
            self.build_zip_file()
            self.egress_assistant.step = EgressStep.DONE
            self.egress_assistant.save()
            self.log_info(_("Successfully exported all selected documents."))

    def on_failed(self, error: Exception) -> None:
        if self.egress_assistant:
            self.egress_assistant.delete()

    def on_stopped(self) -> None:
        if self.egress_assistant:
            self.egress_assistant.delete()
