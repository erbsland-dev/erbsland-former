#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from django.utils.translation import gettext_lazy as _

from backend.splitter.context_source import ContextSource
from backend.syntax_handler.base import SyntaxHandlerBase
from backend.splitter.analysis_window import AnalysisWindow
from backend.splitter.line import Line
from backend.splitter.split_level import SplitLevel


class MarkdownSyntaxHandler(SyntaxHandlerBase):
    """
    A syntax handler for Markdown text.
    """

    name = "markdown"
    verbose_name = _("Markdown")
    accepted_suffixes = ["md", "markdown"]
    markdown_block_identifier = "md"

    @staticmethod
    def is_empty_line(line: Line):
        return line and not line.text.strip()

    @staticmethod
    def is_hash_header(line: Line) -> Optional[SplitLevel]:
        if not line:
            return None
        text = line.text
        if not text.startswith("#"):  # The line must start with `#`
            return None
        for level in range(1, 9):  # Test up to 8 `#` characters, waiting for a white-space.
            if len(text) <= level:
                return None
            if text[level] == "#":
                continue
            if text[level].isspace():
                break
        else:
            return None
        if not text[level + 1 :].strip():  # If no text is after the '#', it is no title.
            return None
        return SplitLevel.get_section(level)

    @staticmethod
    def is_title_underline_line(line: Line) -> Optional[SplitLevel]:
        if not line:
            return None
        text = line.text
        if not text.startswith(("-", "=")):
            return None
        text = text.rstrip()  # Accept white-space at the end of the line.
        for c in text:
            if c != text[0]:  # If there are other characters in the line, it's not a title underline.
                return None
        if text[0] == "=":
            return SplitLevel.SECTION_LEVEL_1
        return SplitLevel.SECTION_LEVEL_2

    def analyze_line(self, analysis_window: AnalysisWindow) -> SplitLevel:
        # Split at headings.
        if split_level := self.is_hash_header(analysis_window.current):
            analysis_window.current.meta.text = analysis_window.current.text.strip(" \t#")
            analysis_window.current.meta.source = ContextSource.SECTION
            return split_level
        if not analysis_window.current.is_empty():
            if split_level := self.is_title_underline_line(analysis_window.next[0]):
                text = analysis_window.current.text.strip(" \t#")
                analysis_window.current.meta.text = text
                analysis_window.current.meta.source = ContextSource.SECTION
                # Make sure the title and its underline are never split.
                analysis_window.next[0].split_level = SplitLevel.KEEP_LINES
                return split_level
        # Split at paragraphs
        if not analysis_window.current.is_indented() and self.is_empty_line(analysis_window.previous[0]):
            return SplitLevel.PARAGRAPH
        return SplitLevel.LINE
