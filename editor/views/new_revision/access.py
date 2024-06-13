#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.utils.translation import gettext_lazy as _

from backend.models import RevisionAssistant, Revision
from editor.views.new_revision.steps import NewRevisionSteps
from backend.enums.new_revision_step import NewRevisionStep
from editor.views.project import ProjectAccessMixin
from editor.views.project.assistant_mixin import ProjectAssistantMixin


class NewRevisionAccessMixin(
    ProjectAssistantMixin[NewRevisionSteps, NewRevisionStep, RevisionAssistant], ProjectAccessMixin
):
    steps = NewRevisionSteps()
    page_icon_name = "code-commit"
    assistant_name = "new_revision"
    assistant_model = RevisionAssistant
    assistant_step_enum = NewRevisionStep
    assistant_display_name = _("New Revision")

    def get_revision(self) -> Revision:
        # If an assistant was started, use its stored revision instead of any supplied one.
        # Call `get_assistant` because `self._assistant` isn't initialized at this point.
        assistant = self.get_assistant()
        if assistant:
            return assistant.revision
        return super().get_revision()
