#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from design.views.generic import ConfirmView
from editor.views.egress.access import EgressAccessMixin


class EgressStopView(EgressAccessMixin, ConfirmView):

    form_submit_class = "is-danger is-medium"
    form_submit_icon = "trash"
    form_cancel_icon = "arrow-left"
    form_cancel_class = "is-success is-medium"
    warning_text = _("Are you sure to stop the running export?")

    def get(self, request, *args, **kwargs):
        if not self.assistant:
            # If there is no assistant-instance, it was already cleaned up by the failed/stopped task.
            # In this case, jump back to the project page.
            return redirect(self.get_project_url())
        # If the object still exists, let the user decide if the operation shall be stopped.
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # A post-request means the "Stop" button on the form was clicked.
        if self.assistant:
            self.assistant.delete()
        # TODO: Add notification
        return redirect(self.get_project_url())

    def get_page_icon_name(self) -> str:
        return ""

    def get_page_title_prefix(self) -> str:
        return ""

    def get_page_title(self) -> str:
        return _("Stop Export?")

    def get_form_cancel_text(self) -> str:
        return _("Back")

    def get_form_submit_text(self) -> str:
        return _("Stop Export")

    def get_form_cancel_url(self):
        return self.get_step_url(self.get_current_step_value())
