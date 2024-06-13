#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum
from dataclasses import dataclass

from backend.tools.statistic.statistic_field import StatisticField


@dataclass(frozen=True)
class StatisticValue:
    """
    One value of the statistic.
    """

    field: StatisticField
    """The field definition."""
    text: str
    """The value for that field."""
