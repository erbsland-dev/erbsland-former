#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from backend.enums.egress_step import EgressStep
from design.views.assistant.steps_base import AssistantStepsBase
from design.views.assistant.step_definition import AssistantStepDefinition


class EgressStepDefinition(AssistantStepDefinition[EgressStep]):
    pass


class EgressSteps(AssistantStepsBase[EgressStepDefinition]):
    step_definitions = [
        EgressStepDefinition(EgressStep.SETUP, "egress_setup", _("Setup")),
        EgressStepDefinition(EgressStep.RUNNING, "egress_running", _("Export Running"), is_transition=True),
        EgressStepDefinition(EgressStep.DONE, "egress_done", _("Done")),
    ]
