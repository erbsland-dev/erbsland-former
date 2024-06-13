#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import re
from dataclasses import dataclass
from typing import Optional, Tuple

from backend.splitter.context_source import ContextSource
from backend.syntax_handler.base import SyntaxHandlerBase
from django.utils.translation import gettext_lazy as _

from backend.splitter.analysis_window import AnalysisWindow
from backend.splitter.line import Line
from backend.splitter.split_level import SplitLevel


@dataclass
class HeaderLevel:
    """
    A header level for the document.
    """

    character: str
    """The character that is assigned for the level."""

    split_level: SplitLevel
    """The assigned split level."""


@dataclass
class HeaderRaw:
    """
    A raw header formatting.
    """

    is_header: bool = False
    """If this is a header line."""

    character: str = ""
    """The character that defines the header."""

    length: int = 0
    """The length of the header."""

    def __eq__(self, other):
        if not isinstance(other, HeaderRaw):
            return False
        return self.is_header == other.is_header and self.character == other.character and self.length == other.length


class ReStructuredTextSyntaxHandler(SyntaxHandlerBase):
    """
    A syntax handler for plain text
    """

    name = "reStructuredText"
    verbose_name = _("reStructuredText")
    accepted_suffixes = ["rst"]
    markdown_block_identifier = "rst"

    VALID_SECTION_CHARACTERS = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    RE_DIRECTIVE = re.compile(R"^([ \t]*)\.\. ([-_a-zA-Z0-9]+)::")
    RE_INDENT = re.compile(R"^([ \t]*)[^ \t]")

    def __init__(self):
        self.analysis_window: Optional[AnalysisWindow] = None
        self.header_stack: list[HeaderLevel] = []  # A stack with the headers to build a hierarchy.
        self.header_map: dict[str, HeaderLevel] = {}  # A map to find existing headers.
        self.header_related_lines: list[Line] = []  # Lines like, labels, indexes that belong to following header.
        self.in_directive: str = ""
        self.last_indent_size: int = 0
        self.last_indent_level: int = 1

    @classmethod
    def is_directive(cls, line: str) -> None | Tuple[int, str]:
        """
        Test if the line is a directive.

        :param line: The line
        :return: (number of indentation spaces, directive name)
        """
        if match := cls.RE_DIRECTIVE.match(line):
            return len(match.group(1)), match.group(2)
        return None

    @classmethod
    def is_section_line(cls, line: str) -> HeaderRaw:
        if not line:
            return HeaderRaw()
        stripped_line = line.rstrip()
        length = len(stripped_line)
        result = HeaderRaw(length=length)
        if stripped_line[0] not in cls.VALID_SECTION_CHARACTERS:
            return result
        for character in stripped_line:
            if character != stripped_line[0]:
                return result
        result.character = stripped_line[0]
        result.is_header = True
        return result

    @classmethod
    def is_double_line(cls, results: list[HeaderRaw]) -> bool:
        if len(results) < 3:
            return False
        return (
            results[0].is_header
            and results[0] == results[2]
            and not results[1].is_header
            and 0 < results[1].length <= results[0].length
        )

    @classmethod
    def is_single_line(cls, results: list[HeaderRaw]) -> bool:
        return (
            results[1].is_header
            and not results[0].is_header
            and results[0].length > 3
            and abs(results[0].length - results[1].length) <= 2
        )

    def _is_heading_start(self) -> None | Tuple[str, str]:
        results = [self.is_section_line(line.text) for line in self.analysis_window[:3] if line]
        if len(results) < 2:
            return None

        if self.is_double_line(results):
            self.analysis_window[1].split_level = SplitLevel.KEEP_LINES
            self.analysis_window[2].split_level = SplitLevel.KEEP_LINES
            return results[0].character * 2, self.analysis_window[1].text.strip()

        if self.is_single_line(results):
            self.analysis_window[1].split_level = SplitLevel.KEEP_LINES
            return results[1].character, self.analysis_window.current.text.strip()

        return None

    def _is_just_emptiness_before_current(self) -> None | Line:
        if self.analysis_window.current.line_number > 5:
            return None
        last_empty_line: Optional[Line] = None
        for line in self.analysis_window.previous:
            match line:
                case None:
                    return last_empty_line
                case _ if line.is_empty():
                    last_empty_line = line
                case _:
                    return None
        return last_empty_line

    def _get_level_for_character(self, header_character: str) -> SplitLevel:
        if header_character not in self.header_map:
            if len(self.header_stack) >= 8:
                return SplitLevel.PARAGRAPH
            split_level = SplitLevel.get_section(len(self.header_stack) + 1)
            header_level = HeaderLevel(header_character, split_level)
            self.header_stack.append(header_level)
            self.header_map[header_character] = header_level
        return self.header_map[header_character].split_level

    def _shall_ignore_formatting(self) -> bool:
        return self.in_directive in ["code-block", "sourcecode", "comment", "raw"]

    def _handle_indentation_levels(self):
        if self.analysis_window.current.is_empty():
            return
        match = self.RE_INDENT.match(self.analysis_window.current.text)
        if not match:
            return
        size = len(match.group(1))
        if size == 0:
            self.last_indent_size = 0
            self.last_indent_level = 1
            self.in_directive = ""  # Non-indented text ends any directive.
            return
        if self._shall_ignore_formatting():
            return  # Ignore any level changes for blocks that can contain unknown formatting.
        if size == self.last_indent_size:
            return
        if size < self.last_indent_size:
            self.last_indent_level -= 1
        else:
            self.last_indent_level += 1
        # Malformed text will confuse the levels, reset it to 2.
        if self.last_indent_level < 2:
            self.last_indent_level = 2

    def _paragraph_or_line(self) -> SplitLevel:
        if (
            self.analysis_window.previous[0]
            and self.analysis_window.previous[0].is_empty()
            and not self.analysis_window.current.is_empty()
        ):
            return SplitLevel.PARAGRAPH

        return SplitLevel.LINE

    def _handle_directives(self) -> Optional[SplitLevel]:
        directive = self.is_directive(self.analysis_window.current.text)
        if not directive:
            return None

        indent, name = directive
        if indent == 0:
            if name.startswith("_") or name == "index":
                self.header_related_lines.append(self.analysis_window.current)
            self.analysis_window.current.meta.block = name
            self.in_directive = name
            self.last_indent_size = 0
            self.last_indent_level = 1
            return SplitLevel.BLOCK_LEVEL_1  # Split above of directives.

        if self._shall_ignore_formatting():
            return None  # Do not further process directives inside special blocks.

        # In any other case, return the current level, but do not update the outer directive.
        return SplitLevel.get_block(self.last_indent_level)

    def _handle_in_directive(self) -> Optional[SplitLevel]:
        if not self.in_directive:
            return None
        if self._shall_ignore_formatting():
            return self._paragraph_or_line()

        # While we are in a directive, keep parameter lines together
        if self.analysis_window.current.text.lstrip().startswith(":"):
            return SplitLevel.KEEP_LINES
        return self._paragraph_or_line()

    def _handle_headers(self) -> Optional[SplitLevel]:
        heading = self._is_heading_start()
        if not heading:
            return None
        character, section_title = heading
        split_level = self._get_level_for_character(character)
        lines = [line for line in self.header_related_lines if self.analysis_window.is_line_in_window(line)]
        if line := self._is_just_emptiness_before_current():
            lines.append(line)
        lines.append(self.analysis_window.current)
        line = min(lines, key=lambda x: x.line_number)
        self.header_related_lines = []
        self.in_directive = ""
        line.meta.text = section_title
        line.meta.source = ContextSource.SECTION
        if line == self.analysis_window.current:
            return split_level
        line.split_level = split_level
        return SplitLevel.PARAGRAPH

    def analyze_line(self, analysis_window: AnalysisWindow) -> SplitLevel:
        self.analysis_window = analysis_window
        self._handle_indentation_levels()
        if split_level := self._handle_directives():
            return split_level
        if split_level := self._handle_in_directive():
            return split_level
        if split_level := self._handle_headers():
            return split_level
        return self._paragraph_or_line()
