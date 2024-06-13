#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC
from dataclasses import dataclass
from typing import Optional, Callable, Self


class FractionBarCount:
    """
    One entry in the fraction bar.
    """

    def __init__(self, *, name: str, count: int, color_class: str, label: str | Callable[[Self], str]):
        self.name = name
        self.count = count
        self.color_class = color_class
        self._label = label

    def get_label(self) -> str:
        return self._label % {"count": self.count}


@dataclass
class FractionBarCounts(ABC):
    """
    An object holding the data to display a bar with different fractions.
    """

    def __init__(self) -> None:
        self._counts: list[FractionBarCount] = []
        self._count_map: dict[str, FractionBarCount] = {}

    def __len__(self):
        return len(self._counts)

    def __getitem__(self, key: str) -> FractionBarCount:
        return self._count_map[key]

    def add_count(
        self, name: str, count: int, color_class: str, label: str | Callable[[FractionBarCount], str]
    ) -> None:
        entry = FractionBarCount(name=name, count=count, color_class=color_class, label=label)
        self._counts.append(entry)
        self._count_map[name] = entry

    def has_count(self, name: str) -> bool:
        return name in self._count_map

    def get_count(self, name: str) -> Optional[FractionBarCount]:
        if name not in self._count_map:
            return None
        return self._count_map[name]

    def get_count_value(self, name: str) -> int:
        """
        Get the actual count for a given entry.

        :param name: The name of the entry.
        :return: The count or zero if not found.
        """
        if name not in self._count_map:
            return 0
        return self._count_map[name].count

    @property
    def as_list(self) -> list[FractionBarCount]:
        return self._counts

    @property
    def total_count(self) -> int:
        return sum(count.count for count in self._counts)
