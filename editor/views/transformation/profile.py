#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Tuple

from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from backend.enums import TransformerStatus
from backend.enums.transformation_step import TransformationStep
from backend.models import TransformationAssistant, TransformationAssistantDocument, Fragment
from design.views.checks import CheckList, CheckState
from design.views.generic import FormView
from editor.views.session import SESSION_TRANSFORMATION_LAST_PROFILE
from editor.views.transformation.access import TransformationAccessMixin


class TransformationProfileForm(forms.ModelForm):
    """
    A custom form to select the transformation profile.
    """

    def __init__(self, *args, user: User = None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["profile"].queryset = user.transformer_profiles

    class Meta:
        model = TransformationAssistant
        fields = ["profile"]
        help_texts = {
            "profile": _("Select the transformer profile you would like to use for this transformation."),
        }


class TransformationProfileView(TransformationAccessMixin, FormView):
    """
    The view set up a new transformation for the project.
    """

    template_name = "editor/transformation/profile.html"
    form_class = TransformationProfileForm

    def is_assistant_required(self):
        return False

    def get_form(self, form_class=None) -> TransformationProfileForm:
        last_data = self.request.session.get(SESSION_TRANSFORMATION_LAST_PROFILE, None)
        if not last_data:
            transformer_profiles = self.request.user.transformer_profiles
            if transformer_profiles.exists():
                last_data = {"profile": transformer_profiles.latest("created")}
            else:
                last_data = {}
        form = TransformationProfileForm(
            user=self.request.user,
            initial=last_data,
            data=self.request.POST or None,
            instance=self.assistant,
        )
        return form

    def get_success_url(self):
        return self.get_step_url(TransformationStep.SETUP)

    def has_transformer_profiles(self) -> bool:
        """
        Check if the user has any transformer profiles defined.
        """
        return self.request.user.transformer_profiles.exists()

    def get_form_submit_text(self) -> str:
        if self.check_results.has_warnings:
            return _("Ignore Warnings and Continue")
        return _("Continue")

    def get_form_submit_class(self) -> str:
        if self.check_results.has_errors:
            return "is-danger"
        if self.check_results.has_warnings:
            return "is-warning"
        return "is-success"

    def get_form_submit_icon(self) -> str:
        return "play"

    def is_form_submit_enabled(self) -> bool:
        return not self.check_results.has_errors

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)
        if self.project.has_unfinished_tasks():
            raise ValueError(_("There is already a task running for this project."))
        with transaction.atomic():
            if self.assistant:
                # Update the profile.
                form.save(commit=True)
            else:
                # Create the transformation assistant.
                self.create_assistant_instance(profile=form.cleaned_data["profile"], step=TransformationStep.SETUP)
                # Add the selected documents to the assistant.
                for index, document in enumerate(self._get_selected_documents_from_session()):
                    TransformationAssistantDocument.objects.create(
                        transformation_assistant=self.assistant,
                        order_index=index,
                        document=document,
                    )
        return self.form_valid(form)

    def add_checks(self, check_list: CheckList) -> None:
        self.add_selected_document_check(check_list)
        if not self.has_transformer_profiles():
            check_list.add(
                CheckState.ERROR,
                _("You have no transformer profiles defined yet."),
            )
        has_transformations = (
            Fragment.objects.filter(document__revision=self.revision).filter(transformation__isnull=False).exists()
        )
        if has_transformations:
            check_list.add(CheckState.WARNING, _("Some fragments have already been transformed."))
        else:
            check_list.add(CheckState.OK, _("No fragment is transformed."))
        has_edits = Fragment.objects.filter(document__revision=self.revision).filter(edit__isnull=False).exists()
        if has_edits:
            check_list.add(CheckState.WARNING, _("Some fragments have been edited."))
        else:
            check_list.add(CheckState.OK, _("No fragment has edits."))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"has_transformer_profiles": self.has_transformer_profiles()})
        return context
