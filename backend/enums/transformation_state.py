#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum
from typing import Self

from backend.tools.fraction_bar import FractionBarCounts


class TransformationState(enum.StrEnum):
    SOURCE = "source"
    """The fragment is its source state."""
    SUCCESS = "success"
    """The fragment was successfully transformed."""
    FAILED = "failed"
    """The transformation failed."""
    EDITED = "edited"
    """There is a manual edit for the fragment."""


class TransformationStateCounts(FractionBarCounts):
    """
    A class to count transformation states.
    """

    STATES_IN_ORDER = [
        TransformationState.SOURCE,
        TransformationState.SUCCESS,
        TransformationState.FAILED,
        TransformationState.EDITED,
    ]

    STATE_COLOR_CLASSES = {
        TransformationState.SOURCE: "has-background-unprocessed-light",
        TransformationState.SUCCESS: "has-background-approved-light",
        TransformationState.FAILED: "has-background-rejected-light",
        TransformationState.EDITED: "has-background-warning-light",
    }

    def __init__(self, initialize_with_zero: bool = False):
        super().__init__()
        if initialize_with_zero:
            for state in self.STATES_IN_ORDER:
                self.add_count_for_state(state, 0)

    def add_other(self, other) -> None:
        if not isinstance(other, TransformationStateCounts):
            raise TypeError("Cannot add TransformationStateCounts with other types.")
        for state in self.STATES_IN_ORDER:
            entry = self.get_count(state.name)
            entry.count += other.get_count(state.name).count

    def add_count_for_state(self, state: TransformationState, count: int):
        self.add_count(state.name, count, self.STATE_COLOR_CLASSES[state], f"{state.value.title()}: %(count)d")

    @classmethod
    def from_dict(cls, d: dict[TransformationState, int]) -> Self:
        result = cls()
        for state in cls.STATES_IN_ORDER:
            result.add_count_for_state(state, d.get(state, 0))
        return result
