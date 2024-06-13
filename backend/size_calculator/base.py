#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import abstractmethod

from backend.tools.extension import Extension


class SizeCalculatorBase(Extension):
    """
    A tool to calculate the size of a text fragment.
    """

    unit_name = ""
    """A short name for the unit. E.g. 100 Tokens."""

    maximum_block_size = 1_000_000
    """The maximum size of a block, in bytes, to be held in memory to do the size calculation."""

    def get_unit_name(self) -> str:
        """Get the short name of the unit to be displayed in the user interface."""
        return self.unit_name

    def get_maximum_block_size(self) -> int:
        """Get the maximum block size in bytes, this size calculator can process."""
        return self.maximum_block_size

    def get_minimum_fragment_size_recommendation(self) -> int:
        """Get the minimum fragment size recommendation."""
        return 0

    def get_maximum_fragment_size_recommendation(self) -> int:
        """Get the minimum fragment size recommendation."""
        return 1000

    @abstractmethod
    def size_for_text(self, text: str) -> int:
        """
        Calculate the size for the given text fragment.

        :param text: The text fragment.
        :return: The size.
        """
        pass
