#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import importlib
import importlib.util
import logging
import re
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Type, TypeVar, Generic, Tuple

from backend.tools.extension.extension import Extension
from backend.tools.regular_expressions import RE_VALID_IDENTIFIER

T = TypeVar("T", bound=Extension)


logger = logging.getLogger(__name__)


class ExtensionManager(ABC, Generic[T]):
    """
    A generic extension manager.
    """

    RE_MODULE_NAME_IN_ERROR = re.compile(r"^No module.+'([-_0-9a-z.]+?)'$", re.IGNORECASE)

    def __init__(self):
        self._loaded_extension_names: list[str] = []
        self._choices: list[Tuple[str, str]] = []

    def load_extensions(self, base_class: Type[T], namespace: str):
        """
        Load the extensions from the application.

        Calls `add_extension` for each found class.

        :param base_class: The base class to search for.
        :param namespace: The (sub) namespace in the application to search for classes.
        """
        from django.apps import apps

        if not apps.ready:
            raise ValueError("This extension manager is initialized too early, before all apps are ready.")

        # Load built-ins
        self.load_builtin_extensions()
        # Load extensions from the apps.
        for app in apps.get_app_configs():
            if app.name == "backend":
                continue  # Ignore this app.
            module_name = f"{app.name}.{namespace}"
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError as error:
                if match := self.RE_MODULE_NAME_IN_ERROR.search(str(error)):
                    if match.group(1) != module_name:
                        raise  # Another module was not found, while loading the extension.
                continue  # Ignore this package of its namespace is not defined.
            except ImportError:
                raise  # If the module could not be loaded, stop here.
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                # If there is a method called "register_extensions" call it.
                if callable(attribute) and attribute.__name__ == "register_extensions":
                    attribute(self)
                    continue
                # Check if the attribute is a class, a subclass of the given base class.
                if not (isinstance(attribute, type) and issubclass(attribute, base_class)):
                    continue  # Skip any classes that are no subclasses of the base class.
                if attribute.__name__.endswith("Base"):
                    continue  # Skip any classes name ending in `...Base`
                if self.shall_load_extension(attribute.name):
                    self.add_extension_class(attribute)
        logger.debug(
            f"Registered the following {base_class.__name__} extensions: " + ", ".join(self._loaded_extension_names)
        )
        self.after_loading_extensions()

    def add_extension_names(self, name: str, verbose_name: str) -> None:
        """
        Add the extension names for the loaded extension list and choices field.

        Must be called from `add_extension_class()`.

        :param name: The name of the extension (e.g. class name).
        :param verbose_name: The verbose name of the extension for display.
        """
        if not RE_VALID_IDENTIFIER.match(name):
            raise ValueError(f"The extension name '{name}' is not a valid identifier.")
        self._loaded_extension_names.append(name)
        self._choices.append((name, verbose_name))

    def load_builtin_extensions(self) -> None:
        """
        Register all built-in extensions.

        This can be done via `add_extension_class()` or `add_extension_instance()`.
        """
        pass

    def shall_load_extension(self, name: str) -> bool:
        """
        Method to check if an extension shall be loaded.

        :param name: The name of the extension.
        :return: `True` to load the extension, `False` to skip it.
        """
        return True

    def is_extension_loaded(self, name: str) -> bool:
        """
        Test if an extension is loaded.

        :param name: The name of the extension.
        :return: `True` if loaded, `False` if not.
        """
        return name in self._loaded_extension_names

    @abstractmethod
    def add_extension_class(self, extension_class: Type[T]) -> None:
        """
        Adds the extension with the given class to the manager.

        The implementation must call `add_extension_names()` to register the names of the extensions.

        :param extension_class: The extension class.
        """
        pass

    def after_loading_extensions(self) -> None:
        """
        Called after loading all extensions.
        """
        pass

    @cached_property
    def extension_names(self) -> list[str]:
        """
        Get a list with all extension names.
        """
        return self._loaded_extension_names

    def get_default_name(self) -> str:
        """
        Get a default extension name, e.g. to be used as default value in a database.
        """
        if self._loaded_extension_names:
            return self._loaded_extension_names[0]
        return ""

    def get_choices(self) -> list[Tuple[str, str]]:
        """
        Get a list of choices, to be used in a selection field.
        """
        return self._choices
