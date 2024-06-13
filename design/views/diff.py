#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import difflib
import enum
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


class DiffLineMode(enum.StrEnum):
    """
    The mode of a unified diff line.
    """

    MATCH = "match"
    DELETE = "delete"
    ADD = "add"
    CHANGE = "change"


class DiffResult(ABC):
    """
    The base class for a diff result.
    """

    def __init__(self):
        self.src_label: str = "Source"  # The label of the source file.
        self.dst_label: str = "Destination"  # The label of the destination file.
        self.match_count: int = 0  # The number of matching lines.
        self.delete_count: int = 0  # The number of deleted lines.
        self.add_count: int = 0  # The number of added lines.
        self.total_changes: int = 0  # The total number of changes.

    @property
    def has_no_changes(self) -> bool:
        return self.total_changes == 0

    @abstractmethod
    def start_hunk(self, hidden: bool = False):
        """
        Start a new hunk

        :param hidden: If this hunk shall be hidden by default.
        """
        pass

    @abstractmethod
    def add_match(self, text: str, src_line: int, dst_line: int) -> None:
        """
        Add a match to the current hunk.

        :param text: The text content of the match.
        :param src_line: The line number in the source file.
        :param dst_line: The line number in the destination file.
        """
        pass

    @abstractmethod
    def add_delete(self, text: str, src_line: int) -> None:
        """
        Add a line to the current hunk with DELETE mode.

        :param text: The text of the line to be deleted.
        :param src_line: The line number in the source file of the line to be deleted.
        """
        pass

    @abstractmethod
    def add_add(self, text: str, dst_line: int) -> None:
        """
        Add a line to the current hunk with ADD mode.

        :param text: A string representing the text of the line.
        :param dst_line: An integer representing the line number where the text should be added
        """
        pass


@dataclass
class UnifiedLine:
    """
    One line in a unified diff
    """

    mode: DiffLineMode
    """The mode of the line."""

    text: str
    """The text of the line."""

    src_line: int = None
    """The line number of the source line."""

    dst_line: int = None
    """The line number of the destination line."""


@dataclass
class UnifiedLineHunk:
    """
    A hunk of a unified diff
    """

    lines: list[UnifiedLine] = field(default_factory=list)
    """The lines in the diff."""

    hidden: bool = False
    """If this hunk shall be hidden, as it only consists of matches."""


class UnifiedDiff(DiffResult):
    """
    The unified diff of two texts
    """

    def __init__(self):
        super().__init__()
        self.hunks: list[UnifiedLineHunk] = []  # The hunks in this diff
        self._current_hunk: Optional[UnifiedLineHunk] = None

    def start_hunk(self, hidden: bool = False):
        self._current_hunk = UnifiedLineHunk(hidden=hidden)
        self.hunks.append(self._current_hunk)

    def add_match(self, text: str, src_line: int, dst_line: int) -> None:
        self._current_hunk.lines.append(
            UnifiedLine(mode=DiffLineMode.MATCH, text=text, src_line=src_line, dst_line=dst_line)
        )
        self.match_count += 1

    def add_delete(self, text: str, src_line: int) -> None:
        self._current_hunk.lines.append(UnifiedLine(mode=DiffLineMode.DELETE, text=text, src_line=src_line))
        self.delete_count += 1
        self.total_changes += 1

    def add_add(self, text: str, dst_line: int) -> None:
        self._current_hunk.lines.append(UnifiedLine(mode=DiffLineMode.ADD, text=text, dst_line=dst_line))
        self.add_count += 1
        self.total_changes += 1


RE_HUNK = re.compile(r"^@@\s+-(\d+)(?:,\d+)?\s+\+\d+(?:,\d+)?\s+@@.*$")


def _diff(
    result: DiffResult,
    src_text: str,
    dst_text: str,
    src_line: Optional[int],
    dst_line: Optional[int],
    src_label: Optional[str],
    dst_label: Optional[str],
) -> None:
    """
    Create a diff for the given texts.

    :param result: The result to fill.
    :param src_text: The source text.
    :param dst_text: The destination text.
    :param src_line: Optional source start line number.
    :param dst_line: Optional destination start line number.
    :param src_label: Optional label for the source.
    :param dst_label: Optional label for the destination.
    """
    if not src_line or not isinstance(src_line, int):
        src_line = 1
    if not dst_line or not isinstance(dst_line, int):
        dst_line = src_line
    src_lines = src_text.splitlines()
    dst_lines = dst_text.splitlines()
    if src_label:
        result.src_label = src_label
    if dst_label:
        result.dst_label = dst_label
    src_index = 0
    dst_index = 0
    if src_text != dst_text:
        diff_result = difflib.unified_diff(src_lines, dst_lines, lineterm="")
        initial_skip = 2
        for diff_line in diff_result:
            if initial_skip > 0:
                initial_skip -= 1
                continue
            if match := RE_HUNK.match(diff_line):
                hunk_src_start = int(match.group(1)) - 1
                if hunk_src_start > src_index:
                    result.start_hunk(hidden=True)
                    while hunk_src_start > src_index:
                        result.add_match(src_lines[src_index], src_index + src_line, dst_index + dst_line)
                        src_index += 1
                        dst_index += 1
                result.start_hunk()
            elif len(diff_line) == 0 or diff_line[0] == " ":
                result.add_match(src_lines[src_index], src_index + src_line, dst_index + dst_line)
                src_index += 1
                dst_index += 1
            elif diff_line[0] == "-":
                result.add_delete(src_lines[src_index], src_index + src_line)
                src_index += 1
            elif diff_line[0] == "+":
                result.add_add(dst_lines[dst_index], dst_index + dst_line)
                dst_index += 1
            else:
                raise RuntimeError(f"Unrecognized line start from `difflib.unified_diff`: {diff_line}")
    if src_index < len(src_lines):
        result.start_hunk(hidden=True)
        while src_index < len(src_lines):
            result.add_match(src_lines[src_index], src_index + src_line, dst_index + dst_line)
            src_index += 1
            dst_index += 1


def unified_diff(
    src_text: str,
    dst_text: str,
    *,
    src_line: int = None,
    dst_line: int = None,
    src_label: str = None,
    dst_label: str = None,
) -> UnifiedDiff:
    """
    Create a unified diff from the two given texts.

    :param src_text: The source text.
    :param dst_text: The destination text.
    :param src_line: The fist line number of the source text.
    :param dst_line: The fist line number of the destination text.
    :param src_label: Optional label for the source text.
    :param dst_label: Optional label for the destination text.
    :return: A list of unified lines objects to be rendered.
    """
    result = UnifiedDiff()
    _diff(result, src_text, dst_text, src_line, dst_line, src_label, dst_label)
    return result


@dataclass
class SplitLine:
    """
    One line in a split diff
    """

    src_line: int = None
    """The line number of the source line."""

    src_text: str = None
    """The source line text."""

    dst_line: int = None
    """The line number of the destination line."""

    dst_text: str = None
    """The destination line text."""

    is_match: bool = False
    """If this line is a match."""


@dataclass
class SplitLineHunk:
    """
    A hunk of a unified diff
    """

    lines: list[SplitLine] = field(default_factory=list)
    """The lines in the diff."""

    hidden: bool = False
    """If this hunk shall be hidden, as it only consists of matches."""


class SplitDiff(DiffResult):
    """
    The split diff of two texts
    """

    def __init__(self):
        super().__init__()
        self.hunks: list[SplitLineHunk] = []  # The hunks in this diff
        self._current_hunk: Optional[SplitLineHunk] = None
        self._last_add_in_hunk: int = 0

    def start_hunk(self, hidden: bool = False):
        """
        Start a new hunk

        :param hidden: If this hunk shall be hidden by default.
        """
        self._current_hunk = SplitLineHunk(hidden=hidden)
        self.hunks.append(self._current_hunk)
        self._last_add_in_hunk = 0

    def add_match(self, text: str, src_line: int, dst_line: int) -> None:
        """
        Add a match to the current hunk.

        :param text: The text content of the match.
        :param src_line: The line number in the source file.
        :param dst_line: The line number in the destination file.
        """
        self._current_hunk.lines.append(
            SplitLine(src_text=text, dst_text=text, src_line=src_line, dst_line=dst_line, is_match=True)
        )
        self.match_count += 1
        self._last_add_in_hunk = len(self._current_hunk.lines)

    def add_delete(self, text: str, src_line: int) -> None:
        """
        Add a line to the current hunk with DELETE mode.

        :param text: The text of the line to be deleted.
        :param src_line: The line number in the source file of the line to be deleted.
        """
        self._current_hunk.lines.append(SplitLine(src_text=text, src_line=src_line))
        self.delete_count += 1
        self.total_changes += 1

    def add_add(self, text: str, dst_line: int) -> None:
        """
        Add a line to the current hunk with ADD mode.

        :param text: A string representing the text of the line.
        :param dst_line: An integer representing the line number where the text should be added
        """
        if len(self._current_hunk.lines) > self._last_add_in_hunk:
            line = self._current_hunk.lines[self._last_add_in_hunk]
            line.dst_line = dst_line
            line.dst_text = text
        else:
            self._current_hunk.lines.append(SplitLine(dst_text=text, dst_line=dst_line))
        self._last_add_in_hunk += 1
        self.add_count += 1
        self.total_changes += 1


def split_diff(
    src_text: str,
    dst_text: str,
    *,
    src_line: int = None,
    dst_line: int = None,
    src_label: str = None,
    dst_label: str = None,
) -> SplitDiff:
    """
    Create a unified diff from the two given texts.

    :param src_text: The source text.
    :param dst_text: The destination text.
    :param src_line: The fist line number of the source text.
    :param dst_line: The fist line number of the destination text.
    :param src_label: Optional label for the source text.
    :param dst_label: Optional label for the destination text.
    :return: A list of unified lines objects to be rendered.
    """
    result = SplitDiff()
    _diff(result, src_text, dst_text, src_line, dst_line, src_label, dst_label)
    return result
