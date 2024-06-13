#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property

from django import forms
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from backend.enums.transformation_step import TransformationStep
from backend.models import Document, Fragment
from design.views.generic import FormView
from editor.views.transformation.access import TransformationAccessMixin


class TransformationPreviewForm(forms.Form):
    submit_text = _("Start Transformation")
    submit_icon = "magic-wand-sparkles"


class TransformationPreview(TransformationAccessMixin, FormView):
    """
    The view to preview the transformations.
    """

    template_name = "editor/transformation/preview.html"
    form_class = TransformationPreviewForm

    def get_form_cancel_text(self) -> str:
        return _("Back")

    def get_form_cancel_icon(self) -> str:
        return "arrow-left"

    def get_form_cancel_url(self):
        if "document_id" in self.kwargs:
            return self.get_step_url(TransformationStep.PREVIEW)
        return self.get_step_url(TransformationStep.SETUP)

    @cached_property
    def selected_documents(self) -> QuerySet[Document]:
        return self.assistant.get_documents_from_fragments(self.selected_fragments)

    @cached_property
    def selected_fragments(self) -> QuerySet[Fragment]:
        return self.assistant.get_selected_fragments()

    @cached_property
    def selected_fragment_count(self) -> int:
        return self.selected_fragments.count()

    def is_form_submit_enabled(self) -> bool:
        return self.selected_fragments.exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "document_id" in self.kwargs:
            document_id = self.kwargs["document_id"]
            document = Document.objects.get(pk=document_id)
            fragments = self.selected_fragments.filter(document=document).order_by("position")
            context.update(
                {
                    "document_id": document_id,
                    "document": document,
                    "fragments": fragments,
                    "fragment_count": fragments.count(),
                }
            )
        else:
            context.update({"documents": self.selected_documents})
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)
        if self.project.has_unfinished_tasks():
            # this shouldn't happen, but prevent it, because it could result in data loss.
            raise ValueError(_("There is already a task running for this project."))
        self.assistant.transform_selected_fragments(
            success_url=self.get_step_url(TransformationStep.DONE),
            failure_url=self.get_step_url(TransformationStep.PREVIEW),
        )
        return self.form_valid(form)
