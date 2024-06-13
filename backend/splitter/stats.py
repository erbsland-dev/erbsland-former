#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass


@dataclass
class SplitterStats:
    """
    Class to collect statistics about the splitting process.
    """

    unit_count: int = 0
    byte_count: int = 0
    character_count: int = 0
    word_count: int = 0
    line_count: int = 0
    fragment_count: int = 0
