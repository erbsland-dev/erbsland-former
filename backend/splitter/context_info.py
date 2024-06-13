#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass
from typing import Self

from backend.splitter.context_source import ContextSource
from backend.splitter.split_location_context import SplitLocationContext
from backend.splitter.split_level import SplitLevel


@dataclass
class NodeContextEntry:
    level: SplitLevel
    source: ContextSource
    text: str

    def __str__(self) -> str:
        return f"{self.level}-{self.source}: {self.text}"


class NodeContextInfo:
    """
    Context information for a node.
    """

    def __init__(self):
        self.entries: list[NodeContextEntry] = []

    def _has_entry(self, level: SplitLevel, source: ContextSource, text: str) -> bool:
        for entry in self.entries:
            if entry.level == level and entry.source == source and entry.text == text:
                return True
        return False

    def merge_location_context(self, split_level: SplitLevel, context: SplitLocationContext):
        if not context.is_empty():
            if not self._has_entry(split_level, context.source, context.text):
                self.entries.append(NodeContextEntry(split_level, context.source, context.text))

    def merge_parent_context(self, context: Self):
        # Prepend the context information from the parent context to build it in the correct order.
        for entry in reversed(context.entries):
            if not self._has_entry(entry.level, entry.source, entry.text):
                self.entries[:0] = [entry]

    def __str__(self) -> str:
        result = "Entries:"
        for entry in self.entries:
            result += f"\n  {entry}"
        return result
