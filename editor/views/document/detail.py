#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, Union

from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend import models
from backend.size_calculator.manager import size_calculator_manager
from backend.syntax_handler import syntax_manager
from design.views.action import ActionDetailView, ActionHandlerResponse
from design.views.paginated import PaginatedChildrenMixin
from design.views.tree_navigation import TreeNavigationMixin, TreeNavigation
from editor.views.document.access import DocumentAccessMixin
from editor.views.fragment.update_review_state_action import UpdateReviewStateMixin


class DocumentView(
    DocumentAccessMixin,
    UpdateReviewStateMixin,
    PaginatedChildrenMixin,
    TreeNavigationMixin,
    ActionDetailView,
):
    model = models.Document
    template_name = "editor/document/detail.html"
    paginator_session_prefix = "editor.document"
    page_icon_name = "file"

    def handle_goto_parent(self) -> ActionHandlerResponse:
        return reverse("project", kwargs={"pk": self.project.pk})

    def handle_goto_next(self) -> ActionHandlerResponse:
        if not self.document_tree.has_next_document(self.object.pk):
            return None
        next_id = self.document_tree.get_next_document_id(self.object.pk)
        return reverse("document", kwargs={"pk": next_id})

    def handle_goto_previous(self) -> ActionHandlerResponse:
        if not self.document_tree.has_previous_document(self.object.pk):
            return None
        previous_id = self.document_tree.get_previous_document_id(self.object.pk)
        return reverse("document", kwargs={"pk": previous_id})

    def get_tree_navigation(self) -> Optional[TreeNavigation]:
        return TreeNavigation(
            has_next=self.document_tree.has_next_document(self.object.pk),
            has_previous=self.document_tree.has_previous_document(self.object.pk),
            next_title=_("Next document"),
            previous_title=_("Previous document"),
            parent_title=_("Back to project"),
        )

    def get_paginator_parent_id(self) -> Union[str, int]:
        return self.document.pk

    def get_paginator_queryset(self) -> QuerySet:
        return self.document.fragments.order_by("position").select_related("edit", "transformation")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "document_syntax": syntax_manager.verbose_name(self.document.document_syntax),
                "size_unit": size_calculator_manager.get_unit_name(self.object.size_unit),
                "has_running_tasks": self.project.has_unfinished_tasks(),
            }
        )
        return context
