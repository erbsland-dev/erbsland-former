#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.urls import reverse

from backend.enums import ReviewState
from backend.models import Fragment
from design.views.action import ActionHandlerResponse


logger = logging.getLogger(__name__)


class UpdateReviewStateMixin:
    def _get_fragment_for_review_state_update(self) -> Fragment:
        if hasattr(self, "fragment"):
            return self.fragment
        if hasattr(self, "document"):
            fragment_id = int(self.request.POST.get("fragment_id"))
            return self.document.fragments.get(pk=fragment_id)
        raise ValueError("Could not access the fragment object.")

    def handle_update_review_state_goto_next(self) -> ActionHandlerResponse:
        return self.handle_update_review_state(goto_next=True)

    def handle_update_review_state(self, goto_next: bool = False) -> ActionHandlerResponse:
        try:
            new_review_state = ReviewState(int(self.action_value))
            with transaction.atomic():
                if not self.project.can_be_edited:
                    return reverse("project_cannot_edit", kwargs=self.project.pk) + f"next={self.request.path}"
                fragment = self._get_fragment_for_review_state_update()
                old_state = fragment.review_state
                fragment.review_state = new_review_state
                fragment.save()
                if goto_next and hasattr(self, "handle_goto_next_review"):
                    return self.handle_goto_next_review(ReviewState(old_state))
        except ValueError or ObjectDoesNotExist as error:
            logger.warning(f"Failed to update the review state. Reason: {error}")
            pass  # Ignore these, as they only occur when the request is tampered with.
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "review_states": [
                    ReviewState.UNPROCESSED,
                    ReviewState.PENDING,
                    ReviewState.REJECTED,
                    ReviewState.APPROVED,
                ],
            }
        )
        if hasattr(self, "fragment"):
            if self.fragment.review_state == ReviewState.PENDING:
                context["review_and_next_states"] = [ReviewState.REJECTED, ReviewState.APPROVED]
            elif self.fragment.review_state == ReviewState.REJECTED:
                context["review_and_next_states"] = [ReviewState.APPROVED]
        return context
