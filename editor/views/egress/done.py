#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.utils.translation import gettext_lazy as _

from design.views.assistant.generic import AssistantDoneView
from editor.views.egress.access import EgressAccessMixin


class EgressDoneView(EgressAccessMixin, AssistantDoneView):
    template_name = "editor/egress/done.html"
    intro_text = _("Your export has been prepared and is ready for download.")

    def get_success_url(self):
        return self.get_project_url()

    def get_form_submit_text(self) -> str:
        return _("Close Assistant and Return to Project")

    def get_form_submit_class(self) -> str:
        return "is-outline"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
