#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse, reverse_lazy

from backend.models import Document, Revision, Project
from backend.size_calculator.manager import size_calculator_manager
from backend.tools.document_tree import DocumentTree
from design.views.breadcrumbs import Breadcrumb
from editor.views.project import ProjectAccessMixin


class DocumentAccessMixin(ProjectAccessMixin):
    def __init__(self, *args, **kwargs):
        self._document: Optional[Document] = None
        super().__init__(*args, **kwargs)

    def initialize_db_objects(self) -> Optional[HttpResponse]:
        try:
            self._document = self.get_document()
            self._revision = self.get_revision()
            self._project = self.get_project()
        except ObjectDoesNotExist:
            return HttpResponseNotFound("The requested document was not found.")
        return None  # No inheritance, because order is reversed.

    def get_document(self) -> Document:
        return Document.objects.get(pk=self.kwargs["pk"])

    @property
    def document(self) -> Document:
        return self._document

    @cached_property
    def document_tree(self) -> DocumentTree:
        return DocumentTree(self.revision)

    def get_revision(self) -> Revision:
        return self.document.revision

    def get_project(self) -> Project:
        return self.revision.project

    def get_object(self, queryset=None):
        # Replace the get object method for document access subclasses.
        return self.document

    @cached_property
    def fragment_count(self) -> int:
        return self.document.fragments.count()

    @cached_property
    def document_size_unit(self) -> str:
        return size_calculator_manager.get_unit_name(self.document.size_unit)

    def get_page_title(self) -> str:
        return self.document.name

    def get_breadcrumbs_title(self) -> str:
        return self.document.get_shortened_name()

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        result = super().get_breadcrumbs().copy()
        result.append(Breadcrumb(self.get_project_title(), self.get_project_url()))
        return result

    def get_context_data(self, **kwargs):
        # Add the context variables to access the document.
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "document": self.document,
                "document_syntax": self.document.document_syntax,
                "fragment_count": lambda: self.fragment_count,
                "size_unit": lambda: self.document_size_unit,
            }
        )
        return context
