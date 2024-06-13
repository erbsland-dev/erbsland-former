#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from design.views.generic import FormView
from .access import IngestAccessMixin


class IngestStopForm(forms.Form):
    submit_text = _("Abort Import")
    submit_class = "is-danger"
    submit_icon = "trash"
    cancel_icon = "arrow-left"
    cancel_class = "is-success"


class IngestStop(IngestAccessMixin, FormView):
    template_name = "design/assistant/modal.html"
    form_class = IngestStopForm
    intro_text = _("Are you sure to stop the current import?")

    def get(self, request, *args, **kwargs):
        if not self.assistant:
            # If there is no ingest-instance, it was already cleaned up by the failed/stopped task.
            # In this case, jump back to the project page.
            return redirect(self.get_project_url())
        # If the object still exists, let the user decide if the ingest operation shall be stopped.
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # A post-request means the "Stop" button on the form was clicked.
        if self.assistant:
            self.assistant.delete()
        # TODO: Add notification
        return redirect(self.get_project_url())

    def get_page_title(self) -> str:
        return _("Stop Import")

    def get_form_cancel_text(self) -> str:
        return _("Back to Assistant")

    def get_form_cancel_icon(self) -> str:
        return "arrow-left"

    def get_form_cancel_url(self):
        return self.get_step_url(self.assistant.step)
