#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from typing import Optional

from backend.splitter.split_location_context import SplitLocationContext
from backend.splitter.split_level import SplitLevel


@dataclass
class SplitLocation:
    """
    A split location in a file.
    """

    location: int
    """The byte location in the read file."""
    line_number: Optional[int]
    """The line number in the read file"""
    split_level: SplitLevel
    """The split level"""
    context: Optional[SplitLocationContext] = None
    """Meta info at this split location."""
    split_index: int = -1  # Set initially to -1 to make sure it is overwritten.
    """The resulting split index from zero as highest to lowest"""
