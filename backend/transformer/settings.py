#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC
from typing import Any

from backend.tools.json_serializable import JsonSerializable


class TransformerSettingsBase(JsonSerializable):
    """
    The base class for transformer settings.
    Derive your transformer profile and user settings from this class.
    """

    pass
