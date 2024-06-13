#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Any, Self


class TaskStatusField:
    """
    A field that displays the portion of the action status.
    """

    JSON_NAME = "name"
    JSON_TITLE = "title"
    JSON_PLACEHOLDER = "placeholder"
    JSON_ICON_NAME = "icon_name"

    def __init__(self, name: str, title: str, placeholder: str = "", icon_name: str = None):
        """
        Create a new task status field.

        :param name: The name of the field.
        :param title: The label of the field displayed in the status.
        :param placeholder: A placeholder if no status is set.
        :param icon_name: An optional icon name that is placed in front of the label.
        """
        self._name = name
        self._title: str = title
        self._placeholder: str = placeholder
        self._icon_name: str = icon_name

    @property
    def name(self) -> str:
        """
        The name of this field, used to reference the value.
        """
        return self._name

    @property
    def title(self) -> str:
        """
        The title of this field displayed in the status.
        """
        return self._title

    @property
    def placeholder(self) -> str:
        """
        A placeholder text displayed if no status is available.
        """
        return self._placeholder

    @property
    def icon_name(self) -> str:
        """
        Optional name of an icon to displayed in front of the title.
        """
        return self._icon_name

    def to_json(self) -> dict[str, Any]:
        # Uses `str()` to force translations to be resolved when added to JSON data.
        return {
            self.JSON_NAME: str(self.name),
            self.JSON_TITLE: str(self.title),
            self.JSON_PLACEHOLDER: str(self.placeholder),
            self.JSON_ICON_NAME: str(self.icon_name or ""),
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return TaskStatusField(
            data[cls.JSON_NAME], data[cls.JSON_TITLE], data[cls.JSON_PLACEHOLDER], data[cls.JSON_ICON_NAME]
        )
