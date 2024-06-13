#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from design.views.generic import FormView


class AssistantEmptyForm(forms.Form):
    pass


class AssistantDoneView(FormView):
    """
    A generic form view.

    Requires to be used with the "AssistantMixin" mixin.
    """

    template_name = "design/assistant/done.html"
    form_class = AssistantEmptyForm

    def form_valid(self, form):
        with transaction.atomic():
            self.assistant.delete()
        return super().form_valid(form)

    def get_page_title(self) -> str:
        return _("%(assistant_name)s Successful") % {"assistant_name": self.get_assistant_display_name()}

    def get_form_submit_text(self) -> str:
        return _("Close Assistant and Continue")

    def get_form_submit_icon(self) -> str:
        return "arrow-right"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = ""
        return context
