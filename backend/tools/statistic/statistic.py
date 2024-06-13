#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from tracemalloc import Statistic
from typing import Self, Any

import humanize

from backend.tools.statistic.statistic_value import StatisticValue
from backend.tools.statistic.statistic_field import StatisticField


class Statistic:
    """
    Statistic to be displayed at the end of the assistant.
    """

    def __init__(self):
        self._values: list[StatisticValue] = []

    @property
    def values(self) -> list[StatisticValue]:
        return self._values

    def add_value(self, value: StatisticValue):
        """
        Add a value to the statistic.

        :param value: The value to be added.
        """
        self._values.append(value)

    def add(self, title: str, value: str | int, icon_name: str = None, name: str = None) -> None:
        """
        Add a new statistic entry.

        :param title: The title of this entry.
        :param value: The value of this entry.
        :param icon_name: The optional name of an icon to display (fas fa-[name])
        :param name: The optional name of this entry.
        """
        self.add_value(StatisticValue(StatisticField(name, title, icon_name), str(value)))

    @classmethod
    def from_fields(cls, fields: list[StatisticField], values: dict[str, Any]) -> Self:
        """
        Create a new statistics object from a list of fields and a dictionary with the values.

        :param fields: A list of the fields.
        :param values: The values for the fields.
        :return: A new statistic object.
        """
        result = cls()
        for field in fields:
            value = values.get(field.name, "")
            if isinstance(value, int):
                text = humanize.intcomma(value)
            elif isinstance(value, float):
                text = f"{value:0.2f}"
            else:
                text = str(value)
            result.add_value(StatisticValue(field, text))
        return result
