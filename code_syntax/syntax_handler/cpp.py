#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import re

from django.utils.translation import gettext_lazy as _

from backend.splitter.context_source import ContextSource
from backend.syntax_handler.base import SyntaxHandlerBase
from backend.splitter.analysis_window import AnalysisWindow
from backend.splitter.split_level import SplitLevel


class CppSyntaxHandler(SyntaxHandlerBase):
    """
    A very simplistic syntax handler for C++ code.

    This syntax handler expects well formatted C++ code that groups its blocks with 2 and 1 empty lines.
    Next are lines that end with an opening bracket, depending on its indent-level.
    It also puts a split after a copyright header, as often it is joined with `#pragma once` or an `#include`
    Contexts are not supported, as this would require a proper token based parser.
    """

    name = "cpp"
    verbose_name = _("C/C++ Code")
    accepted_suffixes = ["h", "hpp", "hxx", "c", "cpp", "cxx"]
    markdown_block_identifier = "cpp"

    RE_OPEN_BRACKET = re.compile(R"^(\s+)\S.*\{(?:\s*//.*?)?$")
    """Match indented lines that end with an open bracket."""

    def analyze_line(self, analysis_window: AnalysisWindow) -> SplitLevel:
        # Test for initial copyright block.
        if not analysis_window.previous[0] and analysis_window.current.text.startswith("//"):
            for line in analysis_window.next:
                if not line:
                    break
                if not line.text.startswith("//"):
                    line.split_level = SplitLevel.BLOCK_LEVEL_1
                    break
        # Test for empty to not empty line transition
        if (
            analysis_window.previous[0]
            and analysis_window.previous[0].is_empty()
            and not analysis_window.current.is_empty()
        ):
            # Check for just one or two empty lines. Ignore an empty line at the beginning of the file.
            if analysis_window.previous[1]:
                if analysis_window.previous[1].is_empty():  # Two or more empty lines.
                    return SplitLevel.BLOCK_LEVEL_1
                else:
                    return SplitLevel.BLOCK_LEVEL_2
        # Test for lines that end in an open bracket.
        if match := self.RE_OPEN_BRACKET.match(analysis_window.current.text):
            spaces = match.group(1)
            spaces = spaces.replace("\t", "    ")
            level = len(spaces) // 4
            if 0 < level <= 5:  # Require at least 4 spaces indention, and up to five levels.
                return SplitLevel.get_block(level + 2)  # Start at block level 3
        # Everything else is just lines.
        return SplitLevel.LINE
