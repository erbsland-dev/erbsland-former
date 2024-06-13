#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import enum


SECTION_BASE = 300
BLOCK_BASE = 400


class SplitLevel(enum.IntEnum):
    """
    This enum defines possible hierarchies of split-level.

    Only use the levels your document syntax implementation actually supports. The only important aspect is that
    you use these levels in the given order, from largest `PART` down to `WORD` which is the smallest.

    I recommend that you either use `PARAGRAPH` and `LINE` or `PARAGRAPH` and `SENTENCE` and/or `WORD`, but do not
    combine `SENTENCE`/`WORD` and `LINE` as these concepts my overlap.
    """

    PART = 101
    """A part is the largest possible block of a document."""

    CHAPTER = 201
    """A chapter"""

    SECTION_LEVEL_1 = SECTION_BASE + 1
    """A section"""
    SECTION_LEVEL_2 = SECTION_BASE + 2
    """A section"""
    SECTION_LEVEL_3 = SECTION_BASE + 3
    """A section"""
    SECTION_LEVEL_4 = SECTION_BASE + 4
    """A section"""
    SECTION_LEVEL_5 = SECTION_BASE + 5
    """A section"""
    SECTION_LEVEL_6 = SECTION_BASE + 6
    """A section"""
    SECTION_LEVEL_7 = SECTION_BASE + 7
    """A section"""
    SECTION_LEVEL_8 = SECTION_BASE + 8
    """A section"""

    BLOCK_LEVEL_1 = BLOCK_BASE + 1
    """A block"""
    BLOCK_LEVEL_2 = BLOCK_BASE + 2
    """A block"""
    BLOCK_LEVEL_3 = BLOCK_BASE + 3
    """A block"""
    BLOCK_LEVEL_4 = BLOCK_BASE + 4
    """A block"""
    BLOCK_LEVEL_5 = BLOCK_BASE + 5
    """A block"""
    BLOCK_LEVEL_6 = BLOCK_BASE + 6
    """A block"""
    BLOCK_LEVEL_7 = BLOCK_BASE + 7
    """A block"""
    BLOCK_LEVEL_8 = BLOCK_BASE + 8
    """A block"""

    PARAGRAPH = 501
    """A paragraph is a block of text consisting of one or more sentences."""

    LINE = 601
    """A line of text"""
    KEEP_LINES = 701
    """Split between two lines of text, but they should be kept together."""

    SENTENCE = 601
    """A single sentence in a paragraph"""
    WORD = 701
    """A single word"""

    def markdown_section_prefix(self) -> str:
        """
        Get the correct number of markdown hash "#" characters in front of a section.

        :return: A string with the given number of "#" characters plus a space, or an empty string.
        """
        if int(self) < (SECTION_BASE + 1) or int(self) > (SECTION_BASE + 8):
            return ""
        return "#" * (int(self) - SECTION_BASE) + " "

    @classmethod
    def get_section(cls, level: int) -> "SplitLevel":
        if not (1 <= level <= 8):
            raise ValueError(f"There is no section with level {level}.")
        return cls(SECTION_BASE + level)

    @classmethod
    def get_block(cls, level: int) -> "SplitLevel":
        if not (1 <= level <= 8):
            raise ValueError(f"There is no block with level {level}.")
        return cls(BLOCK_BASE + level)
