#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property
from typing import Optional

from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend import models
from backend.enums import ReviewState
from backend.models import Fragment
from design.views.action import ActionDetailView, ActionHandlerResponse
from design.views.tree_navigation import TreeNavigationMixin, TreeNavigation
from editor.views.fragment.access import FragmentAccessMixin
from editor.views.fragment.update_review_state_action import UpdateReviewStateMixin


class FragmentViewBase(FragmentAccessMixin, UpdateReviewStateMixin, TreeNavigationMixin, ActionDetailView):
    model = models.Fragment

    def handle_goto_parent(self):
        return reverse("document", kwargs={"pk": self.document.pk})

    def handle_goto_next(self) -> ActionHandlerResponse:
        if not self.has_next:
            return None
        if self.object.position >= (self.document.fragments.count() - 1):
            document_id = self.document_tree.get_next_document_id(self.document.pk)
            document = self.revision.documents.get(pk=document_id)
            next_fragment = document.fragments.earliest("position")
        else:
            next_fragment = self.document.fragments.get(position=self.object.position + 1)
        return redirect(reverse("fragment", kwargs={"pk": next_fragment.pk}))

    def handle_goto_previous(self) -> ActionHandlerResponse:
        if not self.has_previous:
            return None
        if self.object.position <= 0:
            document_id = self.document_tree.get_previous_document_id(self.document.pk)
            document = self.revision.documents.get(pk=document_id)
            previous_fragment = document.fragments.latest("position")
        else:
            previous_fragment = self.document.fragments.get(position=self.object.position - 1)
        return redirect(reverse("fragment", kwargs={"pk": previous_fragment.pk}))

    def handle_goto_next_review(self, state: ReviewState = None) -> ActionHandlerResponse:
        if state is None:
            state = ReviewState(self.fragment.review_state)
        fragments = (
            Fragment.objects.filter(document__revision=self.revision, review_state=state.value)
            .filter(
                Q(document__path=self.document.path, position__gt=self.fragment.position)
                | Q(document__path__gt=self.document.path)
            )
            .order_by("document__path", "position")
        )
        if not fragments.exists():
            return reverse(f"project_no_{state.name.lower()}", kwargs={"pk": self.project.pk})
        return reverse("fragment", kwargs={"pk": fragments.first().pk})

    @cached_property
    def has_next_fragment(self) -> bool:
        return self.object.position < (self.fragment_count - 1)

    @cached_property
    def has_previous_fragment(self) -> bool:
        return self.object.position > 0

    @cached_property
    def has_next(self) -> bool:
        if not self.has_next_fragment:
            return self.document_tree.has_next_document(self.document.pk)
        return True

    @cached_property
    def has_previous(self) -> bool:
        if not self.has_previous_fragment:
            return self.document_tree.has_previous_document(self.document.pk)
        return True

    def get_tree_navigation(self) -> Optional[TreeNavigation]:
        if self.has_next_fragment:
            next_title = _("Next fragment")
        else:
            next_title = _("First fragment in next document")
        if self.has_previous_fragment:
            previous_title = _("Previous fragment")
        else:
            previous_title = _("Last fragment in previous document")
        parent_title = _("Back to Document")
        return TreeNavigation(
            has_next=self.has_next,
            has_previous=self.has_previous,
            has_next_sibling=self.has_next_fragment,
            has_previous_sibling=self.has_previous_fragment,
            next_title=next_title,
            previous_title=previous_title,
            parent_title=parent_title,
        )
