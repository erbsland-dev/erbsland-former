#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum
from dataclasses import dataclass
from typing import Iterator


class CheckState(enum.StrEnum):
    """
    The state of a check point.
    """

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CheckPoint:
    """
    A single check point in a list of checks.
    """

    state: CheckState
    text: str


class CheckList:
    """
    A list of check points.
    """

    def __init__(self):
        self._check_points = []
        self._has_errors = False
        self._has_warnings = False

    def add(self, state: CheckState, text: str) -> None:
        """
        Add a check point.

        :param state: The state of the check.
        :param text: The text of the check.
        """
        if state == CheckState.WARNING:
            self._has_warnings = True
        if state == CheckState.ERROR:
            self._has_errors = True
        self._check_points.append(CheckPoint(state, text))

    @property
    def has_errors(self) -> bool:
        return self._has_errors

    @property
    def has_warnings(self) -> bool:
        return self._has_warnings

    def __iter__(self) -> Iterator[CheckPoint]:
        return self._check_points.__iter__()
