#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend.models import Fragment, Document
from design.views.breadcrumbs import Breadcrumb
from editor.views.document.access import DocumentAccessMixin


class FragmentAccessMixin(DocumentAccessMixin):
    def __init__(self, *args, **kwargs):
        self._fragment: Optional[Fragment] = None
        super().__init__(*args, **kwargs)

    def initialize_db_objects(self) -> Optional[HttpResponse]:
        try:
            self._fragment = self.get_fragment()
        except ObjectDoesNotExist:
            return HttpResponseNotFound("The requested fragment was not found.")
        return super().initialize_db_objects()

    def get_fragment(self) -> Fragment:
        fragment = Fragment.objects.filter(pk=self.kwargs["pk"]).select_related("edit", "transformation").first()
        if not fragment:
            raise Fragment.DoesNotExist
        return fragment

    @property
    def fragment(self) -> Fragment:
        return self._fragment

    @cached_property
    def has_edit(self) -> bool:
        return self.fragment.has_edit

    @cached_property
    def has_transformation(self) -> bool:
        return self.fragment.has_transformation

    def get_document(self) -> Document:
        return self.fragment.document

    def get_object(self, queryset=None):
        return self.fragment

    def get_breadcrumbs_title(self) -> str:
        return _("Fragment %(position)d / %(count)d") % {
            "position": self.fragment.position + 1,
            "count": self.fragment_count,
        }

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        breadcrumbs = super().get_breadcrumbs()
        document_title = self.document.name
        document_url = reverse("document", kwargs={"pk": self.document.pk})
        breadcrumbs.append(Breadcrumb(document_title, document_url))
        return breadcrumbs

    def get_context_data(self, **kwargs):
        # Add the context variables to access the document.
        context = super().get_context_data(**kwargs)
        transformation = None
        if self.has_transformation:
            transformation = self.fragment.transformation
        edit = None
        if self.has_edit:
            edit = self.fragment.edit
        context.update(
            {
                "fragment": self.fragment,
                "source_text": self.fragment.text,
                "has_transformation": self.has_transformation,
                "transformation": transformation,
                "has_edit": self.has_edit,
                "has_potential_changes": self.has_edit or self.has_transformation,
                "edit": edit,
            }
        )
        return context
