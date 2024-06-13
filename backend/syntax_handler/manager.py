#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from pathlib import Path
from typing import Union, Type, TypeVar

from django.conf import settings
from django.utils.functional import LazyObject

from backend.splitter.line_reader import FileLineReader
from backend.splitter.text_fragment_node import TextFragmentNode
from backend.tools.extension.extension_manager import T
from backend.tools.extension.class_extension_manager import ClassExtensionManager

logger = logging.getLogger(__name__)


SyntaxHandlerClass = TypeVar("SyntaxHandlerClass", bound="SyntaxHandlerBase")


class SyntaxManager(ClassExtensionManager[SyntaxHandlerClass]):
    """
    The manager to load all document syntax instances from the system.
    """

    def __init__(self):
        super().__init__()
        self.markdown_block_identifier_map: dict[str, str] = {}
        from backend.syntax_handler.base import SyntaxHandlerBase

        self.load_extensions(SyntaxHandlerBase, "syntax_handler")

    def load_builtin_extensions(self) -> None:
        from backend.syntax_handler import PlainTextSyntaxHandler, MarkdownSyntaxHandler, ReStructuredTextSyntaxHandler

        for extension in [PlainTextSyntaxHandler, MarkdownSyntaxHandler, ReStructuredTextSyntaxHandler]:
            self.add_extension_class(extension)

    def shall_load_extension(self, name: str) -> bool:
        return name not in settings.BACKEND_IGNORE_SYNTAX_HANDLER

    def get_default_name(self) -> str:
        if self.is_extension_loaded(settings.BACKEND_DEFAULT_SYNTAX_HANDLER):
            return settings.BACKEND_DEFAULT_SYNTAX_HANDLER
        return "markdown"

    def after_loading_extensions(self) -> None:
        super().after_loading_extensions()
        for extension_class in self.extension_list:
            self.markdown_block_identifier_map[extension_class.name] = extension_class.markdown_block_identifier

    def detect_file_syntax(self, working_path: Path, original_path: Path) -> str:
        """
        Analyse the file and detect its syntax.

        :param working_path: The path to the file contents locally stored for import.
        :param original_path: The original path from the upload.
        :return: The syntax identifier or an empty string if it does not match any.
        """
        for syntax_handler in self._extension_list:
            if syntax_handler.matches_syntax(working_path, original_path):
                return syntax_handler.name
        return ""

    def split_file_into_fragments(self, path: Path, syntax_name: str) -> TextFragmentNode:
        """
        Build a text fragment tree for the given file using the specified syntax.

        :param path: The file.
        :param syntax_name: The name of the syntax to use.
        :return: The root text fragment.
        """
        syntax_handler = self.create_for_name(syntax_name)
        with FileLineReader(path) as line_reader:
            return syntax_handler.split_document_into_fragments(line_reader)

    def get_markdown_block_identifier(self, syntax_name: str) -> str:
        """
        Get the markdown block identifier for the given syntax.

        :param syntax_name: The name of the syntax extension.
        :return: The markdown block identifier.
        """
        return self.markdown_block_identifier_map.get(syntax_name, "")


class LazySyntaxManager(LazyObject):
    """
    A lazy object wrapper around the syntax manager.
    """

    def _setup(self):
        self._wrapped = SyntaxManager()


syntax_manager: Union[SyntaxManager, LazySyntaxManager] = LazySyntaxManager()
"""The global instance of the syntax manager."""
