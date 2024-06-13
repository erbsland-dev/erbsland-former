#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from backend.actions.ingest_base import IngestBase
from backend.enums.ingest_step import IngestStep
from tasks.actions import ActionError


class IngestImportDocuments(IngestBase):
    name = "ingest_import_documents"
    progress_title = _("Importing Documents")
    progress_subject = _("Import")

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)

    def run(self, input_data: dict) -> None:
        self.log_info(_("Start importing the documents."))
        try:
            with transaction.atomic():
                self.set_db_object_from_input_data(input_data)
                if self.ingest_assistant.step != IngestStep.IMPORTING_DOCUMENTS:
                    raise ActionError(_("The ingest operation is in the wrong state."))
                self.revision.documents.filter(is_preview=True).update(is_preview=False)
                self.ingest_assistant.step = IngestStep.DONE
                self.ingest_assistant.save()
            self.log_info(_("Successfully imported the documents."))
        except Exception as error:
            # In case of any error, go back to the setup step.
            self.log_error(_("Failed to import the documents."))
            with transaction.atomic():
                self.ingest_assistant.step = IngestStep.PREVIEW
                self.ingest_assistant.save()
            raise
