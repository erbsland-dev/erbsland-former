#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import TypeVar, Union

from django.utils.functional import LazyObject

from backend.tools.extension.instance_extension_manager import InstanceExtensionManager

TransformerInstance = TypeVar("TransformerInstance", bound="TransformerBase")


class TransformerManager(InstanceExtensionManager[TransformerInstance]):
    """
    The manager to load all transformer instances from the system.
    """

    def __init__(self):
        super().__init__()
        from backend.transformer import TransformerBase

        self.load_extensions(TransformerBase, "transformer")

    def get_version(self, name: str) -> int:
        """
        Get the version of a transformer.

        :param name: The identifier/name of the transformer.
        :return: The version number.
        """
        return self.get_extension(name).version

    def get_transformer(self, name: str) -> TransformerInstance:
        """
        Get the transformer for the given identifier.

        :param name: The identifier/name of the transformer.
        :return: The loaded instance of the transformer.
        """
        return self.get_extension(name)


class LazyTransformerManager(LazyObject):
    """
    A lazy object wrapper around the syntax manager.
    """

    def _setup(self):
        self._wrapped = TransformerManager()


transformer_manager: Union[TransformerManager, LazyTransformerManager] = LazyTransformerManager()
"""The global instance of the transformer manager."""
