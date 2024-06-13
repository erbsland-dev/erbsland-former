#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC
from typing import Type

from backend.tools.extension.extension_manager import ExtensionManager, T


class InstanceExtensionManager(ExtensionManager[T], ABC):
    """
    An extension manager that stored one instance of each extension and returns it on request.
    """

    def __init__(self):
        super().__init__()
        self._extension_map: dict[str, T] = {}
        self._extension_list: list[T] = []

    def add_extension_class(self, extension_class: Type[T]) -> None:
        extension_instance = extension_class()
        self.add_extension_instance(extension_instance)

    def add_extension_instance(self, extension_instance: T) -> None:
        extension_name = extension_instance.get_name()
        self.add_extension_names(extension_name, extension_instance.get_verbose_name())
        self._extension_list.append(extension_instance)
        self._extension_map[extension_name] = extension_instance

    def get_default(self) -> T:
        """Get the default extension."""
        default_name = self.get_default_name()
        if default_name in self._loaded_extension_names:
            return self._extension_map[default_name]

    def get_extension(self, name: str) -> T:
        """
        Get the instance with the given name.

        :param name: The name of the extension.
        :return: The extension instance.
        """
        if name not in self._loaded_extension_names:
            raise ValueError(f'There is no extension with the name "{name}".')
        return self._extension_map[name]

    def verbose_name(self, name: str) -> str:
        """
        Get the verbose name of the given extension.
        """
        if name not in self._extension_map:
            return ""
        return self._extension_map[name].get_verbose_name()
