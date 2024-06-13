#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property

from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from backend.enums import TransformerStatus
from backend.enums.egress_destination import EgressDestination
from backend.enums.egress_step import EgressStep
from backend.models import Fragment
from backend.models.egress_assistant import EgressAssistant
from backend.models.egress_assistant_document import EgressAssistantDocument
from design.views.checks import CheckList, CheckState
from design.views.generic import FormView
from editor.views.egress.access import EgressAccessMixin
from editor.views.session import SESSION_EGRESS_LAST_SETUP


class EgressSetupForm(forms.ModelForm):
    """
    A custom form to select the egress destination.
    """

    DESTINATION_CHOICES = [
        (EgressDestination.ZIP_FILE, _("Export as ZIP Archive")),
    ]

    destination = forms.ChoiceField(choices=DESTINATION_CHOICES)

    class Meta:
        model = EgressAssistant
        fields = ["destination"]


class EgressSetupView(EgressAccessMixin, FormView):
    """
    The view set up a new export of the project.
    """

    template_name = "editor/egress/setup.html"
    form_class = EgressSetupForm

    def is_assistant_required(self):
        return False

    def get_form(self, form_class=None) -> EgressSetupForm:
        last_data = self.request.session.get(SESSION_EGRESS_LAST_SETUP, None)
        form = EgressSetupForm(
            initial=last_data,
            data=self.request.POST or None,
            instance=self.assistant,
        )
        return form

    def get_success_url(self):
        return self.get_step_url(EgressStep.RUNNING)

    def get_form_submit_text(self) -> str:
        if self.check_results.has_errors:
            return _("Start Export")
        if self.check_results.has_warnings:
            return _("Ignore Warnings and Start Export")
        return _("Start Export")

    def is_form_submit_enabled(self) -> bool:
        return not self.check_results.has_errors

    def get_form_submit_icon(self) -> str:
        return "play"

    def get_form_submit_class(self) -> str:
        if self.check_results.has_errors:
            return "is-danger"
        if self.check_results.has_warnings:
            return "is-warning"
        return "is-success"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)
        if self.project.has_unfinished_tasks():
            raise ValueError(_("There is already a task running for this project."))
        # Create/Update the assistant object.
        with transaction.atomic():
            if self.assistant:
                # Update the setup object.
                form.save(commit=True)
            else:
                # Create the egress assistant.
                self.create_assistant_instance(destination=form.cleaned_data["destination"], step=EgressStep.SETUP)
                # Add the selected documents to the assistant.
                for index, document in enumerate(self._get_selected_documents_from_session()):
                    EgressAssistantDocument.objects.create(
                        egress_assistant=self.assistant,
                        order_index=index,
                        document=document,
                    )
        # After updating/creating the assistant object, start the export.
        self.assistant.start_export(
            success_url=self.get_step_url(EgressStep.DONE),
            failure_url=self.get_step_url(EgressStep.SETUP),
        )
        return self.form_valid(form)

    def add_checks(self, check_list: CheckList) -> None:
        self.add_selected_document_check(check_list)
        self.add_latest_revision_warning(check_list)
        self.add_review_check(check_list)
        self.add_transformer_failure_check(check_list)
