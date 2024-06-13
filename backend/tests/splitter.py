#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import logging
from pathlib import Path

from django.test import TestCase

from backend.size_calculator.base import SizeCalculatorBase
from backend.size_calculator.manager import size_calculator_manager
from backend.splitter.block import SplitterBlock
from backend.splitter.line_reader import FileLineReader
from backend.splitter.splitter import Splitter
from backend.splitter.error import SplitterError
from backend.syntax_handler import syntax_manager
from ai_transformer.size_calculator import TokenGpt4SizeCalculator


class SplitterTestCase(TestCase):
    def setUp(self):
        self.log = logging.getLogger(__name__)

    def _get_data_path(self, filename: str) -> Path:
        return Path(__file__).parent / "data" / filename

    def _split_file(
        self, syntax: str, size_handler: str, filename: str, minimum: int, maximum: int
    ) -> list[SplitterBlock]:
        """Split a file into blocks."""
        path = self._get_data_path(filename)
        syntax_handler = syntax_manager.create_for_name(syntax)
        size_calculator = size_calculator_manager.get_extension(size_handler)
        with FileLineReader(path) as line_reader:
            splitter = Splitter(
                line_reader=line_reader,
                syntax=syntax_handler,
                size_calculator=size_calculator,
                minimum_size=minimum,
                maximum_size=maximum,
            )
            blocks = list(splitter)
        return blocks

    def test_small_file(self):
        blocks = self._split_file("markdown", "char", "short_markdown_1.md", 100, 2000)
        # This short file should fit into one single block
        self.assertEqual(len(blocks), 1)
        self.assertLess(blocks[0].size, 2000)
        self.assertGreater(blocks[0].size, 100)
        # The contents of this block must be an exact copy of the file.
        path = self._get_data_path("short_markdown_1.md")
        file_contents = path.read_text(encoding="utf-8")
        self.assertEqual(blocks[0].text, file_contents)

    def test_large_file(self):
        blocks = self._split_file("markdown", "token_gpt4", "flatland-by-edwin-abbott.md", 100, 500)
        # This file is about 200k, what will create mor than 100 blocks with less than 500 tokens.
        path = self._get_data_path("flatland-by-edwin-abbott.md")
        file_contents = path.read_text(encoding="utf-8")
        self.assertGreater(len(blocks), 100)
        self.assertLess(len(blocks), 200)
        block_contents = "".join([block.text for block in blocks])
        self.assertEqual(file_contents, block_contents)
        # Verify the block sizes.
        size_calculator = TokenGpt4SizeCalculator()
        for block in blocks:
            calculated_size = size_calculator.size_for_text(block.text)
            delta = abs(block.size - calculated_size)
            self.assertLess(delta, 20)  # Accept a difference of 20 tokens.
        # Test if there are line numbers and that they are in sequence.
        # Test if each line number exists once.
        line_number = 0
        line_numbers = set()
        for block in blocks:
            self.assertIsInstance(block.line_number, int)
            self.assertGreaterEqual(block.line_number, line_number)
            line_number = block.line_number
            self.assertNotIn(block.line_number, line_numbers)
            line_numbers.add(block.line_number)

    def test_one_line_file(self):
        """Test a file that could cause problems because they are too small to be useful."""
        blocks = self._split_file("plainText", "char", "one_line_file.txt", 100, 2000)
        # This short file should fit into one single block
        self.assertEqual(len(blocks), 1)
        self.assertLess(blocks[0].size, 2000)
        self.assertGreater(blocks[0].size, 100)
        # The contents of this block must be an exact copy of the file.
        path = self._get_data_path("one_line_file.txt")
        file_contents = path.read_text(encoding="utf-8")
        self.assertEqual(blocks[0].text, file_contents)
        # If the task is impossible, the splitter must fail.
        with self.assertRaises(SplitterError):
            blocks = self._split_file("plainText", "char", "one_line_file.txt", 0, 100)

    def test_five_lines_file(self):
        """Test a five line file that could cause problems because they are too small to be useful."""
        blocks = self._split_file("markdown", "char", "five_lines_file.md", 100, 2000)
        # This short file should fit into one single block and the block is smaller than the requested 100 characters.
        self.assertEqual(len(blocks), 1)
        # The contents of this block must be an exact copy of the file.
        path = self._get_data_path("five_lines_file.md")
        file_contents = path.read_text(encoding="utf-8")
        self.assertEqual(blocks[0].text, file_contents)
        # It must be possible to split small files like this
        blocks = self._split_file("markdown", "char", "five_lines_file.md", 0, 50)
        self.assertGreater(len(blocks), 1)

    def test_small_read_size(self):
        """Test what happens if the size calculator can only process small chunks of data."""

        class IncapableSizeCalculator(SizeCalculatorBase):
            name = "incapable_size_calculator"
            verbose_name = "Incapable size calculator"
            maximum_block_size = 1_000

            def size_for_text(self, text: str) -> int:
                if len(text.encode()) > self.maximum_block_size:
                    raise ValueError("Dummy Size Calculator: Got too much data to process.")
                return len(text)

        path = self._get_data_path("flatland-by-edwin-abbott.md")
        syntax_handler = syntax_manager.create_for_name("markdown")
        size_calculator = IncapableSizeCalculator()
        with FileLineReader(path) as line_reader:
            splitter = Splitter(
                line_reader=line_reader,
                syntax=syntax_handler,
                size_calculator=size_calculator,
                minimum_size=100,
                maximum_size=10_000,
            )
            blocks = list(splitter)
        # Now the splitter has to read data in smaller fragments and then reassemble them.
        path = self._get_data_path("flatland-by-edwin-abbott.md")
        file_contents = path.read_text(encoding="utf-8")
        self.assertGreater(len(blocks), 10)
        self.assertLess(len(blocks), 30)
        block_contents = "".join([block.text for block in blocks])
        self.assertEqual(file_contents, block_contents)
        # Verify the block sizes.
        for block in blocks:
            self.assertEqual(block.size, len(block.text))
