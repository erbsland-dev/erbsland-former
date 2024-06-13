#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from abc import ABC
from typing import Optional

from django.utils.translation import gettext_lazy as _

from backend.models.transformation import Transformation
from backend.models.transformation_assistant import TransformationAssistant
from tasks.actions import ActionBase, ActionError


class TransformationBase(ActionBase, ABC):
    """
    The base class of all transformation actions.
    """

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)
        self.transformation_assistant: Optional[TransformationAssistant] = None  # The assistant instance.
        self.transformation: Optional[Transformation] = None  # The transformation object.

    def set_db_object_from_input_data(self, input_data: dict):
        """
        Set the transformation assistant instance from the input data and verify it is valid.

        :param input_data: The input data.
        """
        if "transformation_assistant_pk" not in input_data:
            raise ActionError(_("There was a problem with the input data."))
        transformation_assistant_pk = input_data["transformation_assistant_pk"]
        if not isinstance(transformation_assistant_pk, str):
            raise ActionError(_("There was a problem with the input data."))
        try:
            self.transformation_assistant = TransformationAssistant.objects.get(pk=transformation_assistant_pk)
        except TransformationAssistant.DoesNotExist:
            raise ActionError(_("Could not find the transformation assistant object."))
