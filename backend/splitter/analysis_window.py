#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from collections import deque
from typing import Optional, Iterator

from backend.splitter.line import Line


class AnalysisWindow:
    """
    The analysis window for syntax processors.
    """

    def __init__(self, window_size: int, lines: list[Line]):
        """
        Create a new window with a given window size.

        :param window_size: The window size, how many lines are before and after the current line.
        :param lines: The lines starting from the current line.
        """
        if window_size < 5:
            raise ValueError("Window size must be >= 5")
        if not lines:
            raise ValueError("The `lines` list must not be empty.")
        if len(lines) > (window_size + 1):
            raise ValueError(f"The `lines` must have n <= {window_size + 1} elements.")
        self._window_size: int = window_size
        self._previous: deque[Optional[Line]] = deque([None for _ in range(window_size)])
        self._current: Optional[Line] = lines[0]
        self._next: deque[Optional[Line]] = deque()
        for i in range(1, window_size + 1):
            if i < len(lines):
                self._next.append(lines[i])
            else:
                self._next.append(None)

    @property
    def previous(self) -> deque[Optional[Line]]:
        """The previous lines before the current line. Index 0 is the line directly before `current`."""
        return self._previous

    @property
    def current(self) -> Optional[Line]:
        """The current line."""
        return self._current

    @property
    def next(self) -> deque[Optional[Line]]:
        """The next lines after the current line. Index 0 is the line directly after `current`."""
        return self._next

    def __getitem__(self, index: int) -> None | Line | list[None | Line]:
        """Access the lines using the item syntax."""
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self._next) + 1)
            return [self._get_line_at_index(i) for i in range(start, stop, step)]
        if not isinstance(index, int):
            raise KeyError("Only integer keys or slices are allowed.")
        return self._get_line_at_index(index)

    def _get_line_at_index(self, index: int) -> None | Line:
        if not (-self._window_size <= index <= self._window_size):
            raise KeyError("Index out of range.")
        if index == 0:
            return self._current
        if index < 0:
            return self._previous[abs(index + 1)]
        return self._next[index - 1]

    def is_at_end(self) -> bool:
        """Test if the window reached the end."""
        return not self.current

    def is_line_in_window(self, line: Line):
        """Test if the given line is in this window."""
        return line == self.current or line in self._previous or line in self._next

    def push_line(self, line: Optional[Line]) -> Optional[Line]:
        """
        Push a new line into the analysis window.

        :param line: The new line to push into the window.
        """
        result = self._previous.pop()
        self._previous.appendleft(self._current)
        self._current = self._next.popleft()
        self._next.append(line)
        return result

    def pop_remaining_lines(self) -> Iterator[Line]:
        """
        Pop all remaining lines from the window in the correct order.

        After this call, the window is considered empty.
        """
        if not self.is_at_end():
            raise ValueError("This method must only be called when at end.")
        self._previous.reverse()
        for line in self._previous:
            if line:
                yield line
        # This is also not required, but detects problems in code if used after this method.
        self._previous = deque([None for _ in range(self._window_size)])
