#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from django.test import TestCase

from backend.size_calculator import CharSizeCalculator, ByteSizeCalculator
from ai_transformer.size_calculator.tokens import TokenGpt35TurboSizeCalculator
from ai_transformer.size_calculator.tokens import TokenGpt4SizeCalculator


class SizeCalculatorTestCase(TestCase):
    def test_bytes(self):
        size_calculator = ByteSizeCalculator()
        size = size_calculator.size_for_text("")
        self.assertEqual(size, 0)
        size = size_calculator.size_for_text("x")
        self.assertEqual(size, 1)
        size = size_calculator.size_for_text("😀")
        self.assertEqual(size, 4)
        text = (Path(__file__).parent / "data" / "short_markdown_1.md").read_text(encoding="utf-8")
        expected_size = len(text.encode())
        size = size_calculator.size_for_text(text)
        self.assertEqual(size, expected_size)

    def test_char(self):
        size_calculator = CharSizeCalculator()
        size = size_calculator.size_for_text("")
        self.assertEqual(size, 0)
        size = size_calculator.size_for_text("x")
        self.assertEqual(size, 1)
        size = size_calculator.size_for_text("😀")
        self.assertEqual(size, 1)
        text = (Path(__file__).parent / "data" / "short_markdown_1.md").read_text(encoding="utf-8")
        expected_size = len(text)
        size = size_calculator.size_for_text(text)
        self.assertEqual(size, expected_size)

    def test_token_gpt35(self):
        size_calculator = TokenGpt35TurboSizeCalculator()
        size = size_calculator.size_for_text("")
        self.assertEqual(size, 0)
        size = size_calculator.size_for_text("hello")
        self.assertEqual(size, 1)
        size = size_calculator.size_for_text("😀")
        self.assertLess(size, 4)
        text = (Path(__file__).parent / "data" / "short_markdown_1.md").read_text(encoding="utf-8")
        expected_size = 337  # reference value calculated 2023-09-08
        size = size_calculator.size_for_text(text)
        delta = abs(expected_size - size)
        self.assertLess(delta, 20)

    def test_token_gpt4(self):
        size_calculator = TokenGpt4SizeCalculator()
        size = size_calculator.size_for_text("")
        self.assertEqual(size, 0)
        size = size_calculator.size_for_text("hello")
        self.assertEqual(size, 1)
        size = size_calculator.size_for_text("😀")
        self.assertLess(size, 4)
        text = (Path(__file__).parent / "data" / "short_markdown_1.md").read_text(encoding="utf-8")
        expected_size = 337  # reference value calculated 2023-09-08
        size = size_calculator.size_for_text(text)
        delta = abs(expected_size - size)
        self.assertLess(delta, 20)
