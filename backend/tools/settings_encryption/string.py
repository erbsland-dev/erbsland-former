#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Any, Self

from backend.tools.json_serializable import JsonSerializable
from backend.tools.json_serializable.base import JsonTypes
from backend.tools.settings_encryption.methods import settings_encrypt, settings_decrypt


class EncryptedString(JsonSerializable):
    """
    A string that is automatically encrypted/decrypted when stored in a JSON document.

    :note: If decryption of this string is failing, it acts like an empty string. Therefore, do
    not use empty encrypted strings to store any other state as "not set".
    """
    serialized_name = "EncryptedString"
    serialized_version = 1

    def __init__(self):
        self._text = ""

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        if not isinstance(value, str):
            raise TypeError("`value` must be a string.")
        self._text = value

    def to_json(self, *, add_type=True, add_version=True) -> JsonTypes:
        result = super().to_json(add_type=add_type, add_version=add_version)
        result["encrypted_text"] = settings_encrypt(self._text)
        return result

    @classmethod
    def from_json(cls, json_dict: dict[str, Any], *, version: int = None, verify_type=True) -> Self:
        new_obj = super().from_json(json_dict, version=version, verify_type=verify_type)
        new_obj._text = settings_decrypt(json_dict["encrypted_text"])
        return new_obj

