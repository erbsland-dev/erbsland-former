#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC
from typing import Type

from backend.tools.extension.extension_manager import ExtensionManager, T


class ClassExtensionManager(ExtensionManager[T], ABC):
    """
    An extension manager that stores the extension-classes and instantiate objects from them on request.
    """

    def __init__(self):
        super().__init__()
        self._extension_map: dict[str, Type[T]] = {}
        self._extension_list: list[Type[T]] = []

    def add_extension_class(self, extension_class: Type[T]) -> None:
        self.add_extension_names(extension_class.name, extension_class.verbose_name)
        self._extension_list.append(extension_class)
        self._extension_map[extension_class.name] = extension_class

    def get_default(self) -> Type[T]:
        """
        Get the default extension.
        """
        default_name = self.get_default_name()
        if default_name in self._loaded_extension_names:
            return self._extension_map[default_name]

    def create_for_name(self, name: str) -> T:
        """
        Create an instance of this extension for the given name.

        :param name: The name of the extension.
        :return: The extension instance.
        """
        if name not in self._loaded_extension_names:
            raise ValueError(f'There is no extension with the name "{name}".')
        return self._extension_map[name]()

    def verbose_name(self, name: str) -> str:
        """
        Get the verbose name of the given extension.
        """
        if name not in self._extension_map:
            return ""
        return self._extension_map[name].verbose_name

    @property
    def extension_list(self) -> list[Type[T]]:
        """
        Access the raw list of gathered extension classes.
        """
        return self._extension_list
