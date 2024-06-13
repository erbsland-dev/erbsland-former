#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Self

from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.tools.fraction_bar import FractionBarCounts, FractionBarCount


class ReviewState(models.IntegerChoices):
    """
    The review state a human can assign to a subject.
    """

    UNPROCESSED = 0, _("Unprocessed")
    """The subject was not transformed or edited yet."""
    PENDING = 1, _("Pending")
    """The subject was not reviewed yet."""
    APPROVED = 2, _("Approved")
    """The subject was approved."""
    REJECTED = 3, _("Rejected")
    """The subject was rejected."""

    @property
    def icon_name(self):
        values = {
            self.UNPROCESSED: "equals",
            self.PENDING: "hourglass-half",
            self.APPROVED: "check",
            self.REJECTED: "xmark",
        }
        return values.get(self, "")

    @property
    def action_label(self):
        values = {
            self.UNPROCESSED: _("Unprocessed"),  # That shouldn't be an action.
            self.PENDING: _("Postpone"),
            self.APPROVED: _("Approve"),
            self.REJECTED: _("Reject"),
        }
        return values.get(self, "")


class ReviewStateCounts(FractionBarCounts):
    """
    A class to count review states.
    """

    STATES_IN_ORDER = [ReviewState.UNPROCESSED, ReviewState.PENDING, ReviewState.REJECTED, ReviewState.APPROVED]

    def __init__(self, initialize_with_zero: bool = False):
        super().__init__()
        if initialize_with_zero:
            for state in self.STATES_IN_ORDER:
                self.add_count_for_state(state, 0)

    def add_other(self, other) -> None:
        if not isinstance(other, ReviewStateCounts):
            raise TypeError("Cannot add ReviewStateCounts with other types.")
        for state in self.STATES_IN_ORDER:
            entry = self.get_count(state.name)
            entry.count += other.get_count(state.name).count

    def add_count_for_state(self, state: ReviewState, count: int):
        self.add_count(state.name, count, f"has-background-{state.name.lower()}", f"{state.label}: %(count)d")

    @property
    def has_pending_reviews(self):
        return self.get_count_value(ReviewState.PENDING.name) > 0

    @property
    def has_rejected_reviews(self):
        return self.get_count_value(ReviewState.REJECTED.name) > 0

    @property
    def is_fully_approved(self):
        return self.get_count_value(ReviewState.APPROVED.name) == self.total_count

    @classmethod
    def from_dict(cls, d: dict[ReviewState, int]) -> Self:
        result = ReviewStateCounts()
        for state in cls.STATES_IN_ORDER:
            result.add_count_for_state(state, d.get(state, 0))
        return result
