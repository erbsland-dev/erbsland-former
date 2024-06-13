#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import enum
from abc import ABC
from typing import TypeVar, Generic

AssistantStepEnumType = TypeVar("AssistantStepEnumType", bound=enum.Enum)


class AssistantStepDefinition(ABC, Generic[AssistantStepEnumType]):
    """
    The definition of one step in an assistant.
    """

    EnumType = AssistantStepEnumType

    def __init__(
        self,
        value: AssistantStepEnumType,
        page_name: str,
        label: str = "",
        is_transition: bool = False,
        without_transition: bool = False,
    ):
        """
        Create a new step for an assistant.

        :param value: The enum that is bound to this step.
        :param page_name: The name of the page, that is linked to this step.
        :param label: The label of the step, displayed in the step bar.
        :param is_transition: If true, this step is a transition between two steps. Instead of a label,
            an arrow is displayed for this step. And if the step is active, the arrow is replaced by an
            animated bolt icon.
        :param without_transition: If true, there is no transition between the previous step and this one.
        """
        self._value = value
        self._page_name = page_name
        self._label = label
        self._is_transition = is_transition
        self._without_transition = without_transition

    @property
    def value(self) -> AssistantStepEnumType:
        return self._value

    @property
    def value_name(self) -> str:
        return self._value.name

    @property
    def page_name(self) -> str:
        return self._page_name

    @property
    def label(self) -> str:
        return self._label

    @property
    def is_transition(self) -> bool:
        return self._is_transition

    @property
    def without_transition(self) -> bool:
        return self._without_transition
