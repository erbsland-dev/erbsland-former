#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from pathlib import Path

from django.test import TestCase

from backend.syntax_handler import syntax_manager
from backend.splitter.text_fragment_node import TextFragmentNode


class SyntaxHandlerTestCase(TestCase):
    def setUp(self):
        self.log = logging.getLogger(__name__)

    def test_manager(self):
        """
        Test if the manager has loaded all required syntax handlers for this test.
        """
        name_list = syntax_manager.extension_names
        self.assertIn("markdown", name_list)
        self.assertIn("plainText", name_list)
        self.assertIn("python", name_list)
        self.assertIn("reStructuredText", name_list)
        self.assertIn("cpp", name_list)

    def test_detect(self):
        path = Path(__file__).parent / "data" / "short_markdown_1.md"
        name = syntax_manager.detect_file_syntax(path, path)
        self.assertEqual(name, "markdown")

    def _verify_fragments(self, root_node: TextFragmentNode):
        for node in root_node.get_all_nodes():
            self.assertNotEqual(node.begin, node.end)
            if node.sub_fragments:
                self.assertEqual(node.sub_fragments[0].begin, node.begin)
                self.assertEqual(node.sub_fragments[-1].end, node.end)
                for i in range(len(node.sub_fragments) - 1):
                    self.assertEqual(node.sub_fragments[i].end, node.sub_fragments[i + 1].begin)
        leaf_nodes = list([node for node in root_node.get_all_nodes() if not node.sub_fragments])
        min_leaf_size = min(leaf_nodes, key=lambda x: x.size_in_bytes).size_in_bytes
        max_leaf_size = max(leaf_nodes, key=lambda x: x.size_in_bytes).size_in_bytes
        self.log.debug(f"Leaves {len(leaf_nodes)}: size min: {min_leaf_size} max: {max_leaf_size} bytes")

    def test_build_fragment_tree(self):
        path = Path(__file__).parent / "data" / "short_markdown_1.md"
        root_node = syntax_manager.split_file_into_fragments(path, "markdown")
        self._verify_fragments(root_node)

    def test_large_file(self):
        path = Path(__file__).parent / "data" / "flatland-by-edwin-abbott.md"
        root_node = syntax_manager.split_file_into_fragments(path, "markdown")
        self._verify_fragments(root_node)
