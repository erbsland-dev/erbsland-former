#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from abc import ABC
from pathlib import Path
from typing import Optional

from django.utils.translation import gettext_lazy as _

from backend.models.ingest_assistant import IngestAssistant
from backend.models.revision import Revision
from tasks.actions import ActionBase, ActionError


class IngestBase(ActionBase, ABC):
    """
    The base class of all ingest actions.
    """

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)
        self.ingest_assistant: Optional[IngestAssistant] = None
        self.revision: Optional[Revision] = None
        self.working_directory: Optional[Path] = None

    def set_db_object_from_input_data(self, input_data: dict):
        """
        Set the ingest db instance from the input data and verify it is valid.

        :param input_data: The input data.
        """
        if "ingest_pk" not in input_data:
            raise ActionError(_("There was a problem with the input data."))
        ingest_pk = input_data["ingest_pk"]
        if not isinstance(ingest_pk, str):
            raise ActionError(_("There was a problem with the input data."))
        try:
            self.ingest_assistant = IngestAssistant.objects.get(pk=ingest_pk)
            self.revision = self.ingest_assistant.project.get_latest_revision()
        except IngestAssistant.DoesNotExist:
            raise ActionError(_("Could not find the data import object."))
