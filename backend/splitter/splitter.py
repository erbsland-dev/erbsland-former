#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import io
from typing import Optional, Iterator

from django.conf import settings
from django.utils.text import normalize_newlines

from backend.size_calculator.base import SizeCalculatorBase
from backend.splitter.block import SplitterBlock
from backend.splitter.context_info import NodeContextInfo
from backend.splitter.context_source import ContextSource
from backend.splitter.error import SplitterError
from backend.splitter.line_reader import LineReader
from backend.syntax_handler.base import SyntaxHandlerBase
from backend.splitter.text_fragment_node import TextFragmentNode


class Splitter:
    """
    A tool to split files into defined blocks of text.

    Usage:
    ```
    def split_ebslnd_dev_file():
        splitter = Splitter(...)
        for block in splitter:
        ...
    ```
    """

    def __init__(
        self,
        line_reader: LineReader,
        syntax: SyntaxHandlerBase,
        size_calculator: SizeCalculatorBase,
        minimum_size: int,
        maximum_size: int,
        encoding="utf-8",
    ):
        """
        Create a new instance of the splitter tool.

        :param line_reader: A line reader to supply lines to split.
        :param syntax: The syntax to use.
        :param size_calculator: The size calculator to use.
        :param minimum_size: The minimum size of a block (soft limit).
        :param maximum_size: The maximum size of a block (hard limit).
        :param encoding: The encoding for files.
        """
        # Do input value checks.
        if not isinstance(line_reader, LineReader):
            raise ValueError("`line_reader` must be a `LineReader`")
        if not isinstance(syntax, SyntaxHandlerBase):
            raise ValueError("`syntax` must be derived from `SyntaxHandlerBase`")
        if not isinstance(size_calculator, SizeCalculatorBase):
            raise ValueError("`size_calculator` must be derived from `SizeCalculatorBase`")

        self._line_reader = line_reader
        """The line reader to use."""
        self._syntax = syntax
        """A tool that understands the syntax of a file and knows good splitting points."""
        self._size_calculator = size_calculator
        """A calculator to get a size for a chosen unit."""
        self._minimum_block_size = minimum_size
        """The minimum size of a block in the units of 'size calculator'."""
        self._maximum_block_size = maximum_size
        """The maximum size of a block in the units of 'size calculator'."""
        self._encoding = encoding
        """The encoding of the file to convert the binary data into text."""
        self._maximum_read_size = min(
            self._size_calculator.get_maximum_block_size(),
            settings.BACKEND_SIZE_CALCULATION_MAX_BLOCK_SIZE,
        )
        """The maximum size of a data block that is read from the file."""
        self._binary_stream: Optional[io.IOBase] = None
        """The open stream from which the data is read."""
        self._current = SplitterBlock()
        """The current splitter block that is being built."""
        self._start_node: Optional[TextFragmentNode] = None
        """The node that started the text of a new splitter box, to get the correct context."""

    def __iter__(self) -> Iterator[SplitterBlock]:
        """
        Iterate over the blocks in the file.
        """
        root_node = self._syntax.split_document_into_fragments(self._line_reader)
        root_node.fold()  # Remove any redundant nodes left.
        yield from self._process_node(root_node)
        yield from self._handle_block_and_reset()

    def _process_node(self, node: TextFragmentNode) -> Iterator[SplitterBlock]:
        """
        Recursively process a node.

        :param node: The node to process.
        """
        # If we can't process this fragment, process its sub fragments.
        if node.size_in_bytes > self._maximum_read_size:
            if not node.sub_fragments:  # If there are no sub fragments, we got a problem
                raise SplitterError(
                    f"The smallest fragment, with a size of {node.size_in_bytes} bytes did not "
                    f"fit into the read limits of {self._maximum_read_size} bytes."
                )
            total_size = 0
            for sub_node in node.sub_fragments:
                yield from self._process_node(sub_node)
                if not sub_node.size:
                    raise SplitterError("There was an internal error. A processed sub node had no size.")
                total_size += sub_node.size
            node.size = total_size  # After processing all sub fragments, the size is the sum of them.
        else:
            data = self._line_reader.read_block(node.begin, node.size_in_bytes)
            yield from self._calculate_size(node, data)

    def _calculate_size(self, node: TextFragmentNode, data: bytes) -> Iterator[SplitterBlock]:
        """
        Recursively calculate the size of a node.

        :param node: The node to calculate the size for.
        :param data: The data to use for size calculation.
        """
        text = data.decode(encoding=self._encoding)  # Convert the data into text
        text = normalize_newlines(text)  # Normalize all newlines
        node.size = self._size_calculator.size_for_text(text)  # Calculate the size for this node.
        if (self._current.size + node.size) <= self._maximum_block_size:
            if not self._current.line_number:
                self._current.line_number = node.line_number
            self._current.text += text
            self._current.size += node.size
            if not self._start_node:
                self._start_node = node
            return  # The whole node fit into the block, go back iterating the next one.
        # Before descending into smaller text fragments, check if our block is large enough to process.
        # If we don't do this, blocks will span over high-level split points.
        if self._current.size > 0 and self._current.size >= self._minimum_block_size:
            yield from self._handle_block_and_reset()
            # After reset, this whole fragment may fit into the block.
            if node.size <= self._maximum_block_size:
                self._current.line_number = node.line_number
                self._current.text = text
                self._current.size = node.size
                if not self._start_node:
                    self._start_node = node
                return  # Go back iterating over the next one.
        # At this point, this size does not fit into the block, but we have not enough to continue.
        # Therefore, we need to split the text into the next smaller unit.
        if not node.sub_fragments:
            raise SplitterError(
                f"Smallest text fragment, with a size of {node.size} unites is too large "
                f"to fit into of maximum {self._maximum_block_size} units."
            )
        # Process each sub fragment individually.
        for sub_fragment in node.sub_fragments:
            data_begin = sub_fragment.begin - node.begin
            data_end = sub_fragment.end - node.begin
            yield from self._calculate_size(sub_fragment, data[data_begin:data_end])

    def _handle_block_and_reset(self) -> Iterator[SplitterBlock]:
        """
        Send a block of text to the caller and reset the counters.
        """
        if self._current.size > 0:
            sections = []
            blocks = []
            for entry in self._start_node.context.entries:
                if entry.source == ContextSource.SECTION:
                    sections.append(
                        {
                            "title": entry.text,
                            "level": entry.level.name.lower(),
                        }
                    )
                elif entry.source == ContextSource.BLOCK:
                    blocks.append(
                        {
                            "statement": entry.text,
                            "level": entry.level.name.lower(),
                        }
                    )
            context = {"sections": sections, "blocks": blocks}
            self._current.context = context
            yield self._current
        self._current = SplitterBlock()
        self._start_node = None
