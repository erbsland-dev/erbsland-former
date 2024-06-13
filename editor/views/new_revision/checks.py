#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property

from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from backend.enums import TransformerStatus
from backend.enums.new_revision_step import NewRevisionStep
from backend.models import Fragment, RevisionAssistant
from design.views.checks import CheckState, CheckPoint, CheckList
from design.views.generic import FormView
from editor.views.new_revision.access import NewRevisionAccessMixin


class NewRevisionForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()  # Call the base class's clean method first to get the form data
        keep_fragments = cleaned_data.get("keep_fragments")
        copy_review = cleaned_data.get("copy_review")
        if copy_review and not keep_fragments:
            self.add_error(
                "copy_review",
                _(
                    """\
                    This option can only be selected if “Keep all split points from
                    the selected version.” is also selected.
                    """
                ),
            )
        return cleaned_data

    class Meta:
        model = RevisionAssistant
        fields = ["revision_label", "keep_fragments", "copy_review"]
        help_texts = {
            "revision_label": _(
                """\
                The optional revision level is displayed in the revision list. It has no function and 
                is solely provided as reference for your convenience.
                """
            ),
            "keep_fragments": _(
                """\
                If checked, all splits points from the selected version will be kept. That means the
                document fragments will not be recreated based on the changed contents. It also means
                that context information in the new revision may not match the changed content.
                """
            ),
            "copy_review": _(
                """\
                If checked, all current review states are copied into the new revision. Otherwise,
                all fragments will start in “Unprocessed” review state.
                """
            ),
        }


class NewRevisionChecksView(NewRevisionAccessMixin, FormView):
    """
    The page displaying the checks for a new revision.
    """

    template_name = "editor/new_revision/checks.html"
    form_class = NewRevisionForm

    def add_checks(self, check_list: CheckList) -> None:
        if self.revision.is_latest:
            check_list.add(CheckState.OK, _("You are creating a new revision based on the latest one."))
        else:
            check_list.add(CheckState.WARNING, _("You are restoring an older revision."))
        self.add_review_check(check_list)
        self.add_transformer_failure_check(check_list)
        self.add_unprocessed_fragments_check(check_list)

    def is_assistant_required(self):
        return False

    def get_form(self, form_class=None) -> NewRevisionForm:
        form = NewRevisionForm(data=self.request.POST or None, instance=self.assistant)
        return form

    def get_form_submit_text(self) -> str:
        if self.check_results.has_warnings:
            return _("Ignore Warnings and Create New Revision")
        return _("Create new Revision")

    def is_form_submit_enabled(self) -> bool:
        return not self.check_results.has_errors

    def get_form_submit_icon(self) -> str:
        return "arrow-right"

    def get_form_submit_class(self) -> str:
        if self.check_results.has_errors:
            return "is-danger"
        if self.check_results.has_warnings:
            return "is-warning"
        return "is-success"

    def get_success_url(self) -> str:
        return self.get_step_url(NewRevisionStep.RUNNING)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)
        if self.project.has_unfinished_tasks():
            raise ValueError(_("There is already a task running for this project."))
        with transaction.atomic():
            if self.assistant:
                form.save(commit=True)  # Update the existing options.
            else:
                # Create a new assistant.
                self.create_assistant_instance(
                    revision_label=form.cleaned_data["revision_label"],
                    keep_fragments=form.cleaned_data["keep_fragments"],
                    copy_review=form.cleaned_data["copy_review"],
                )
            self.assistant.start_new_revision(
                success_url=self.get_step_url(NewRevisionStep.DONE),
                failure_url=self.get_step_url(NewRevisionStep.CHECKS),
            )
        return self.form_valid(form)
