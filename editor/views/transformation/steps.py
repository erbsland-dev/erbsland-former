#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from backend.enums.transformation_step import TransformationStep
from design.views.assistant.steps_base import AssistantStepsBase
from design.views.assistant.step_definition import AssistantStepDefinition


class TransformationStepDefinition(AssistantStepDefinition[TransformationStep]):
    pass


class TransformationSteps(AssistantStepsBase[TransformationStepDefinition]):
    step_definitions = [
        TransformationStepDefinition(TransformationStep.PROFILE, "transformation_profile", _("Profile")),
        TransformationStepDefinition(
            TransformationStep.SETUP, "transformation_setup", _("Setup"), without_transition=True
        ),
        TransformationStepDefinition(
            TransformationStep.PREVIEW, "transformation_preview", _("Preview"), without_transition=True
        ),
        TransformationStepDefinition(
            TransformationStep.TRANSFORMATION_RUNNING,
            "transformation_running",
            _("Running"),
            is_transition=True,
        ),
        TransformationStepDefinition(TransformationStep.DONE, "transformation_done", _("Done")),
    ]
