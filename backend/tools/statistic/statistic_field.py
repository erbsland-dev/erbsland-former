#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass

from backend.tools.statistic.statistic_highlight import StatisticHighlight


@dataclass(frozen=True)
class StatisticField:
    """
    The field definition for a statistic entry.
    """

    name: str
    """The name of the field as reference."""
    title: str
    """A title for the field, displayed on the interface."""
    icon_name: str = None
    """An optional icon name, displayed in front of the title."""
    highlight: StatisticHighlight = StatisticHighlight.NONE
    """If this field shall be highlighted."""

    def get_text_color(self):
        match self.highlight:
            case StatisticHighlight.NONE:
                return ""
            case StatisticHighlight.BAD:
                return "has-text-danger-40"
            case StatisticHighlight.GOOD:
                return "has-text-success-40"

    def get_background_color(self):
        match self.highlight:
            case StatisticHighlight.NONE:
                return ""
            case StatisticHighlight.BAD:
                return "has-background-danger-90"
            case StatisticHighlight.GOOD:
                return "has-background-success-90"
