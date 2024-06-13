#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from dataclasses import dataclass
from typing import Union, Type, TypeVar

from django.conf import settings
from django.utils.functional import LazyObject

from backend.tools.extension.extension_manager import T
from backend.tools.extension.instance_extension_manager import InstanceExtensionManager

logger = logging.getLogger(__name__)


SizeCalculatorClass = TypeVar("SizeCalculatorClass", bound="SizeCalculatorBase")


@dataclass
class DefaultSizes:
    bytes_utf8: int
    characters: int
    words: int
    lines: int


class SizeCalculatorManager(InstanceExtensionManager[SizeCalculatorClass]):
    """
    The manager to load all size calculator instances from the system.
    """

    def __init__(self):
        super().__init__()
        from backend.size_calculator.base import SizeCalculatorBase

        self.load_extensions(SizeCalculatorBase, "size_calculator")

    def load_builtin_extensions(self) -> None:
        from backend.size_calculator import (
            ByteSizeCalculator,
            CharSizeCalculator,
            WordSizeCalculator,
            LineSizeCalculator,
        )

        for extension in [ByteSizeCalculator, CharSizeCalculator, WordSizeCalculator, LineSizeCalculator]:
            self.add_extension_class(extension)

    def shall_load_extension(self, name: str) -> bool:
        return name not in settings.BACKEND_IGNORE_SIZE_CALCULATOR

    def get_default_name(self) -> str:
        if self.is_extension_loaded(settings.BACKEND_DEFAULT_SIZE_CALCULATOR):
            return settings.BACKEND_DEFAULT_SIZE_CALCULATOR
        return "char"

    def get_unit_name(self, name: str) -> str:
        """
        Get the display name for the unit of a calculator.

        :param name: The name of the size calculator.
        :return: The unit name associated with the given size calculator.
        """
        return self.get_extension(name).get_unit_name()

    def default_sizes_for_text(self, text: str) -> DefaultSizes:
        """
        Calculate all default sizes in one step.

        :param text: The text for which default sizes need to be calculated.
        :return: A default sizes instance.
        """
        return DefaultSizes(
            bytes_utf8=self.get_extension("bytes_utf8").size_for_text(text),
            characters=self.get_extension("char").size_for_text(text),
            words=self.get_extension("word").size_for_text(text),
            lines=self.get_extension("line").size_for_text(text),
        )


class LazySizeCalculatorManager(LazyObject):
    """
    A lazy object wrapper for the size calculator manager.
    """

    def _setup(self):
        self._wrapped = SizeCalculatorManager()


size_calculator_manager: Union[SizeCalculatorManager, LazySizeCalculatorManager] = LazySizeCalculatorManager()
"""The global instance of the size calculator manager."""
