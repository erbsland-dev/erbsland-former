#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from backend.size_calculator.base import SizeCalculatorBase


class ByteSizeCalculator(SizeCalculatorBase):
    """
    A size calculator that calculates the number of bytes for a UTF-8 encoded string.
    """

    name = "bytes_utf8"
    unit_name = _("Bytes")
    verbose_name = _("Bytes UTF-8")

    def size_for_text(self, text: str) -> int:
        return len(text.encode())


class CharSizeCalculator(SizeCalculatorBase):
    name = "char"
    unit_name = _("Characters")
    verbose_name = _("Characters")

    def size_for_text(self, text: str) -> int:
        return len(text)


class WordSizeCalculator(SizeCalculatorBase):
    name = "word"
    unit_name = _("Words")
    verbose_name = _("Words (Text separated by space)")

    def size_for_text(self, text: str) -> int:
        return len(text.split())


class LineSizeCalculator(SizeCalculatorBase):
    name = "line"
    unit_name = _("Lines")
    verbose_name = _("Lines")

    def size_for_text(self, text: str) -> int:
        return len(text.splitlines(keepends=False))
