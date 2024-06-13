#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from design.views.assistant.generic import AssistantDoneView
from design.views.generic import FormView
from editor.views.new_revision.access import NewRevisionAccessMixin


class NewRevisionDoneView(NewRevisionAccessMixin, AssistantDoneView):
    intro_text = _("A new revision has been successfully created in the project.")

    def get_success_url(self):
        # Don't use `get_project_url()`, as we like to show the latest version of the project.
        return reverse("project", kwargs={"pk": self.project.pk})

    def get_page_title(self) -> str:
        return _("Success")

    def get_form_submit_text(self) -> str:
        return _("Close Assistant and Open New Revision")
