#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum

from django.db import transaction
from django.urls import reverse
from django.utils.text import normalize_newlines
from django.utils.translation import gettext_lazy as _

from design.views.action import ActionHandlerResponse
from design.views.breadcrumbs import Breadcrumb
from editor.views.fragment.base import FragmentViewBase


class FragmentEditView(FragmentViewBase):
    template_name = "editor/fragment/edit/index.html"

    @transaction.atomic()
    def handle_edit_save(self) -> ActionHandlerResponse:
        if not self.fragment.has_edit:
            return  # Wrong state
        text: str = normalize_newlines(self.request.POST.get("edit_text", default=""))
        notes: str = normalize_newlines(self.request.POST.get("edit_notes", default=""))
        self.fragment.set_edit_text(text, notes=notes)
        return reverse("fragment", kwargs={"pk": self.fragment.pk})

    def handle_edit_cancel(self) -> ActionHandlerResponse:
        return reverse("fragment", kwargs={"pk": self.fragment.pk})

    def handle_edit_delete(self) -> ActionHandlerResponse:
        return reverse("fragment_delete_edit", kwargs={"pk": self.object.pk})

    def get_breadcrumbs_title(self) -> str:
        return _("Edit")

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append(
            Breadcrumb(super().get_breadcrumbs_title(), reverse("fragment", kwargs={"pk": self.fragment.pk}))
        )
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
