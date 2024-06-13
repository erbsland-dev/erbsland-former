#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import Optional

from backend.splitter.analysis_window import AnalysisWindow
from backend.splitter.line import Line


class LineReader(ABC):
    """
    A class to be used as context manager to read a document line by line
    """

    @abstractmethod
    def read_line(self) -> Optional[Line]:
        """
        Read a single line from the document.

        :return: A `Line` instance or `None` at the end of the document.
        """
        pass

    @abstractmethod
    def read_block(self, position: int, size: int) -> bytes:
        """
        Read a block of data from the document.

        Calling this method moves the file pointer, and `read_line` will continue after the
        read block.

        :param position: The start position in bytes.
        :param size: The size to read in bytes.
        :return: The read bytes.
        """
        pass

    @property
    @abstractmethod
    def document_size(self) -> int:
        """
        Get the size of the document in bytes.

        This method is used to set the end of the last fragment, therefore it has to be the byte position
        after the last byte of the document.

        :return: The size of the document in bytes.
        """
        pass

    def create_initial_window(self, window_size: int) -> AnalysisWindow:
        """
        Create the initial buffer for the given window size.

        :param window_size: The window size, how many previous and next lines surrounding the read position.
        :return: The list with the initial window.
        """
        lines: list[Optional[Line]] = list([self.read_line() for _ in range(window_size + 1)])
        return AnalysisWindow(window_size, lines)


class FileLineReader(LineReader):
    """
    An implementation to read a document from a file.
    """

    def __init__(self, path: Path, encoding="utf-8"):
        self.fp = None
        self.path = path
        self.encoding = encoding
        self.line_number = 1

    def __enter__(self) -> "LineReader":
        self.fp = self.path.open("rb")
        if not self.fp.seekable():
            raise ValueError("Not seekable stream.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.fp:
            self.fp.close()

    def read_line(self) -> Optional[Line]:
        location = self.fp.tell()
        contents = self.fp.readline(100_000)  # Max 100KB per line.
        if not contents:
            return None
        text = contents.decode(self.encoding, errors="replace").strip("\r\n")
        result = Line(line_number=self.line_number, file_location=location, text=text)
        self.line_number += 1
        return result

    def read_block(self, position: int, size: int) -> bytes:
        self.fp.seek(position)
        return self.fp.read(size)

    @cached_property
    def document_size(self) -> int:
        return self.path.lstat().st_size
