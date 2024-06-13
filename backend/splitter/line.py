#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from backend.splitter.split_location_context import SplitLocationContext
from backend.splitter.split_level import SplitLevel


class Line:
    """
    A single read line with its start location.
    """

    def __init__(self, line_number: int, file_location: int, text: str):
        """
        Create a new line instance.

        :param line_number: The line number.
        :param file_location: The location in the file.
        :param text: The text of the line without newline.
        """
        self._line_number = line_number
        """The line number."""
        self._file_location = file_location
        """The location in the file."""
        self._text = text
        """The text of the line."""

        self.split_level: Optional[SplitLevel] = None
        """The split level is assigned while processing a file line by line."""
        self.meta = SplitLocationContext()

    @property
    def line_number(self) -> int:
        return self._line_number

    @property
    def location(self) -> int:
        return self._file_location

    @property
    def text(self) -> str:
        return self._text

    def is_empty(self) -> bool:
        """Test if this line is empty."""
        return len(self._text.strip()) == 0

    def is_indented(self) -> bool:
        """Test if the line starts with white-space."""
        return not self.is_empty() and self._text[0].isspace()
