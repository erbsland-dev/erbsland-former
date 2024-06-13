#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

from backend.splitter.context_source import ContextSource


@dataclass
class SplitLocationContext:
    """
    Metainformation about a split location.

    Only add metainformation where required to high level elements like sections and blocks.
    """

    text: str = ""
    """The text for the context."""

    source = ContextSource.SECTION
    """The source for the context text."""

    def is_empty(self) -> bool:
        return not self.text
