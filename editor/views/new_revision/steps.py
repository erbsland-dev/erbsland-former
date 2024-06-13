#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from backend.enums.new_revision_step import NewRevisionStep
from design.views.assistant.steps_base import AssistantStepsBase
from design.views.assistant.step_definition import AssistantStepDefinition


class NewRevisionStepDefinition(AssistantStepDefinition[NewRevisionStep]):
    pass


class NewRevisionSteps(AssistantStepsBase[NewRevisionStepDefinition]):
    step_definitions = [
        NewRevisionStepDefinition(NewRevisionStep.CHECKS, "new_revision_checks", _("Checks")),
        NewRevisionStepDefinition(NewRevisionStep.RUNNING, "new_revision_running", _("Running"), is_transition=True),
        NewRevisionStepDefinition(NewRevisionStep.DONE, "new_revision_done", _("Done")),
    ]
