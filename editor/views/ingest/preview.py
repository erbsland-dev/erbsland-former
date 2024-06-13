#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property
from typing import Union

from django import forms
from django.db.models import QuerySet, When, Value, Case
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from backend.enums.ingest_step import IngestStep
from backend.models.document import Document
from backend.size_calculator.manager import size_calculator_manager
from design.views.action import ActionFormView, ActionHandlerResponse
from design.views.paginated import PaginatedChildrenMixin
from .access import IngestAccessMixin
from ..session import SESSION_DOCUMENT_INDEX


class IngestPreviewForm(forms.Form):
    submit_text = _("Import Files")
    submit_icon = "play"


class IngestPreview(IngestAccessMixin, PaginatedChildrenMixin, ActionFormView):
    template_name = "editor/ingest/preview.html"
    form_class = IngestPreviewForm
    paginator_session_prefix = "editor.ingest.preview"

    def handle_document_previous(self) -> ActionHandlerResponse:
        if self.document_index > 0:
            self.document_index -= 1
        return None

    def handle_document_next(self) -> ActionHandlerResponse:
        if self.document_index < self.document_count - 1:
            self.document_index += 1
        return None

    def handle_document_select(self) -> ActionHandlerResponse:
        try:
            document_pk = int(self.action_value)
        except ValueError:
            return None
        for index, document in enumerate(self.documents):
            if document.pk == document_pk:
                self.document_index = index
                break
        return None

    def handle_submit(self):
        form = IngestPreviewForm(data=self.request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return self.get_step_url(IngestStep.IMPORTING_DOCUMENTS)

    @cached_property
    def documents(self) -> QuerySet[Document]:
        revision = self.project.get_latest_revision()
        # The following query set makes sure files in the root directory are sorted before any other paths.
        return (
            Document.objects.filter(revision=revision, is_preview=True)
            .annotate(
                is_root=Case(When(path__contains="/", then=Value(1)), default=Value(0)),
                path_lower=Lower("path"),
            )
            .order_by("is_root", "path_lower")
        )

    @cached_property
    def document_count(self) -> int:
        return self.documents.count()

    @property
    def document_index(self):
        value = self.request.session.get(SESSION_DOCUMENT_INDEX, 0)
        if not value or not isinstance(value, int) or not (0 <= value <= 10_000):
            return 0
        return value

    @document_index.setter
    def document_index(self, value: int):
        self.request.session[SESSION_DOCUMENT_INDEX] = value

    @cached_property
    def document(self):
        document_index = self.document_index
        if 0 <= document_index < len(self.documents):
            for index, document in enumerate(self.documents):  # slow but reliable
                if index == document_index:
                    return document
        return self.documents.first()

    def get_paginator_parent_id(self) -> Union[str, int]:
        return self.document.pk

    def get_paginator_queryset(self) -> QuerySet:
        return self.document.fragments.order_by("position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "documents": self.documents,
                "document": self.document,
                "document_number": self.document_index + 1,
                "document_count": self.document_count,
                "size_unit": size_calculator_manager.get_unit_name(self.document.size_unit),
            }
        )
        return context

    def form_valid(self, form):
        self.assistant.import_previewed_documents(
            success_url=self.get_step_url(IngestStep.DONE),
            failure_url=self.get_step_url(IngestStep.PREVIEW),
        )
        return super().form_valid(form)
