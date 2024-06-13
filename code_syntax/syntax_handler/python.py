#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import re

from backend.splitter.analysis_window import AnalysisWindow
from backend.splitter.context_source import ContextSource
from backend.splitter.split_level import SplitLevel
from backend.syntax_handler.base import SyntaxHandlerBase
from django.utils.translation import gettext_lazy as _


class PythonSyntaxHandler(SyntaxHandlerBase):
    """
    A syntax handler for plain text
    """

    name = "python"
    verbose_name = _("Python Code")
    accepted_suffixes = ["py"]
    markdown_block_identifier = "py"

    RE_BLOCK_START = re.compile(r"^(\s*)(?:def|class|if|elif|else|for|while|try|except|with|match|case)\b")

    def __init__(self):
        self.current_indent_level = 1
        self.indent_space_counts = [0]

    @staticmethod
    def _find_first_non_space_char(text: str) -> int:
        for index, char in enumerate(text):
            if not char.isspace():
                return index
        return 0

    def analyze_line(self, analysis_window: AnalysisWindow) -> SplitLevel:
        line = analysis_window.current.text
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):  # Ignore comments and empty lines
            return SplitLevel.LINE
        line = line.replace("\t", "    ")  # Convert tabs to four spaces.
        # Follow indent levels
        indent_space_count = self._find_first_non_space_char(line)
        assert indent_space_count >= 0
        if indent_space_count == 0:  # Reset case.
            self.indent_space_counts = [0]
        elif indent_space_count > self.indent_space_counts[-1]:
            self.indent_space_counts.append(indent_space_count)
        elif indent_space_count < self.indent_space_counts[-1]:
            # Remove indent counts smaller/equal than the current one, then append the current one.
            # While there are simpler solutions, this algorithm also deals with incorrectly formatted files.
            while self.indent_space_counts[-1] >= indent_space_count:
                self.indent_space_counts.pop()
            self.indent_space_counts.append(indent_space_count)
        else:
            pass  # Ignore the indent level if there is no change to the previous one.
        self.current_indent_level = len(self.indent_space_counts)
        # Detect block start for the first six indent levels
        if self.current_indent_level <= 6 and self.RE_BLOCK_START.match(line):
            analysis_window.current.meta.source = ContextSource.BLOCK
            analysis_window.current.meta.text = analysis_window.current.text.strip()
            return SplitLevel.get_block(self.current_indent_level)
        # Everything else is just lines.
        return SplitLevel.LINE
