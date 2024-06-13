#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABCMeta


class ExtensionMeta(ABCMeta):
    """
    A custom metaclass for the extensions, to make sure `name` is set.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if cls.__name__ != "Extension" and not cls.__name__.endswith("Base"):
            for class_variable in ["name", "verbose_name"]:
                if not namespace.get(class_variable, "").strip():
                    raise TypeError(f"{cls.__name__} must have a non-empty '{class_variable}' class variable.")
        return cls


class Extension(metaclass=ExtensionMeta):
    """
    A generic extension that is dynamically loaded from installed apps.
    """

    name = ""
    """The technical identifier of the extension to be stored in the database or configuration."""

    verbose_name = ""
    """A verbose name of the extension to be displayed in a user interface."""

    def get_name(self) -> str:
        """Get the name of this extension."""
        return self.name

    def get_verbose_name(self) -> str:
        """Get the verbose name of the extension."""
        return self.verbose_name
