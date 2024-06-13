#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from backend.enums.egress_step import EgressStep
from backend.models import Revision
from backend.models.egress_assistant import EgressAssistant
from editor.views.egress.steps import EgressSteps
from editor.views.project import ProjectAccessMixin
from editor.views.project.assistant_mixin import ProjectAssistantMixin


class EgressAccessMixin(ProjectAssistantMixin[EgressSteps, EgressStep, EgressAssistant], ProjectAccessMixin):
    steps = EgressSteps()
    stop_page_name = "egress_stop"
    assistant_name = "egress"
    assistant_model = EgressAssistant
    assistant_step_enum = EgressStep
    assistant_display_name = _("Export")

    def get_revision(self) -> Revision:
        # If an assistant was started, use its stored revision instead of any supplied one.
        # Call `get_assistant` because `self._assistant` isn't initialized at this point.
        assistant = self.get_assistant()
        if assistant:
            return assistant.revision
        return super().get_revision()
