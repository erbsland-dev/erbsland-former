#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass
from typing import Optional, Type

from django import forms
from django.forms import modelformset_factory, BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from backend import models
from backend.enums.ingest_step import IngestStep
from backend.enums.ingest_planed_action import IngestPlanedAction
from backend.size_calculator.base import SizeCalculatorBase
from backend.size_calculator.manager import size_calculator_manager
from backend.syntax_handler import syntax_manager
from design.views.generic import FormView
from editor.views.ingest.access import IngestAccessMixin
from editor.views.session import SESSION_INGEST_LAST_SETUP


@dataclass
class SizeUnitDetails:
    name: str
    verbose_name: str
    unit_name: str
    minimum_fragment_size: int
    maximum_fragment_size: int


class IngestSetupForm(forms.ModelForm):
    submit_text = _("Generate Preview")
    submit_icon = "play"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documents: Optional[Type[BaseModelFormSet]] = None
        choices = size_calculator_manager.get_choices()
        self.fields["size_unit"].widget = forms.Select(choices=choices)
        # Set min and max values for minimum_fragment_size and maximum_fragment_size fields
        self.fields["minimum_fragment_size"].widget.attrs.update({"min": 0, "max": 1000000})
        self.fields["maximum_fragment_size"].widget.attrs.update({"min": 0, "max": 1000000})

    class Meta:
        model = models.IngestAssistant
        fields = ["size_unit", "minimum_fragment_size", "maximum_fragment_size"]
        help_texts = {
            "size_unit": _("Choose the unit of measure for the minimum and maximum size values below."),
        }


class IngestSetup(IngestAccessMixin, FormView):
    template_name = "editor/ingest/setup.html"
    form_class = IngestSetupForm

    def get_ingest_document_form_set_class(self) -> Type[BaseModelFormSet]:
        choices = syntax_manager.get_choices()
        choices.append(("", _("Unknown Syntax")))
        return modelformset_factory(
            model=models.IngestDocument,
            exclude=["ingest", "local_path"],
            extra=0,
            widgets={"document_syntax": forms.Select(choices=choices)},
        )

    def get_document_form_set(self) -> forms.BaseFormSet:
        IngestDocumentFormSet = self.get_ingest_document_form_set_class()
        form_set = IngestDocumentFormSet(
            data=self.request.POST or None,
            queryset=self.assistant.documents.order_by("folder", "name").all(),
            prefix="document",
        )
        return form_set

    def get_form(self, form_class=None) -> IngestSetupForm:
        last_data = self.request.session.get(SESSION_INGEST_LAST_SETUP, None)
        if not last_data:
            default_size_calculator: SizeCalculatorBase = size_calculator_manager.get_default()
            last_data = {
                "size_unit": default_size_calculator.get_name(),
                "minimum_fragment_size": default_size_calculator.get_minimum_fragment_size_recommendation(),
                "maximum_fragment_size": default_size_calculator.get_maximum_fragment_size_recommendation(),
            }
        form = IngestSetupForm(
            initial=last_data,
            data=self.request.POST or None,
            instance=self.assistant,
            prefix="ingest",
        )
        form.documents = self.get_document_form_set()
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid() and form.documents.is_valid():
            form.save()
            form.documents.save()
            if not self.assistant.documents.filter(planed_action=IngestPlanedAction.ADD).exists():
                form.add_error(
                    field=None,
                    error=_("At least one file has to be selected to be added in this import."),
                )
                return self.form_invalid(form)
            document: forms.ModelForm
            for document in form.documents:
                document_path = document.cleaned_data["folder"].strip() + "/" + document.cleaned_data["name"].strip()
                if (
                    self.assistant.project.get_latest_revision()
                    .documents.filter(path__iexact=document_path, is_preview=False)
                    .exists()
                ):
                    document.add_error(
                        field="name",
                        error=_("A document with this path already exists in the current revision."),
                    )
                    return self.form_invalid(form)
            self.request.session[SESSION_INGEST_LAST_SETUP] = form.cleaned_data
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.assistant.generate_preview(
            success_url=self.get_step_url(IngestStep.PREVIEW),
            failure_url=self.get_step_url(IngestStep.SETUP),
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        size_unit_details: list[SizeUnitDetails] = []
        for name in size_calculator_manager.extension_names:
            size_calculator: SizeCalculatorBase = size_calculator_manager.get_extension(name)
            size_unit_details.append(
                SizeUnitDetails(
                    name=name,
                    verbose_name=size_calculator.get_verbose_name(),
                    unit_name=size_calculator.get_unit_name(),
                    minimum_fragment_size=size_calculator.get_minimum_fragment_size_recommendation(),
                    maximum_fragment_size=size_calculator.get_maximum_fragment_size_recommendation(),
                )
            )
        context["size_unit_details"] = size_unit_details
        return context
