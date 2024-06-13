#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from backend.enums import ReviewState
from backend.enums.transformation_step import TransformationStep
from backend.enums.transformed_states import TransformedStates
from backend.models.transformation_assistant import TransformationAssistant
from design.views.generic import FormView
from editor.views.transformation.access import TransformationAccessMixin


class TransformationSetupForm(forms.ModelForm):
    """
    A custom form with just the upload field.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = TransformationAssistant
        fields = [
            "transformed_states",
            "review_unprocessed",
            "review_pending",
            "review_approved",
            "review_rejected",
            "stop_consecutive_failures",
            "stop_total_failures",
            "rollback_on_failure",
            "auto_approve_unchanged",
        ]
        labels = {
            "review_unprocessed": _("Unprocessed"),
            "review_pending": _("Pending"),
            "review_approved": _("Approved"),
            "review_rejected": _("Rejected"),
            "transformed_states": _("Changes"),
            "stop_consecutive_failures": _("Consecutive Failures"),
            "stop_total_failures": _("Total Failures"),
            "rollback_on_failure": _("Rollback on Failure"),
            "auto_approve_unchanged": _("Automatically approve transformed fragments with no changes."),
        }


class TransformationSetup(TransformationAccessMixin, FormView):
    """
    The view set up a new transformation for the project.
    """

    template_name = "editor/transformation/setup.html"
    form_class = TransformationSetupForm

    def get_form_submit_text(self) -> str:
        return _("Preview Transformation")

    def get_form_submit_icon(self) -> str:
        return "play"

    def get_form(self, form_class=None) -> TransformationSetupForm:
        form = TransformationSetupForm(data=self.request.POST or None, instance=self.assistant)
        return form

    def form_valid(self, form):
        form.save()
        self.assistant.step = TransformationStep.PREVIEW
        self.assistant.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        failure_choices = [(0, _("Ignore"))]
        for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50, 75, 100]:
            failure_choices.append((n, str(n)))
        context["failure_choices"] = failure_choices
        return context
