#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC
from typing import TypeVar, Generic

from design.views.assistant.step_definition import AssistantStepDefinition, AssistantStepEnumType

AssistantStepType = TypeVar("AssistantStepType", bound=AssistantStepDefinition)


class AssistantStepsBase(ABC, Generic[AssistantStepType]):
    step_definitions: list[AssistantStepType] = []
    """The predefined list of steps for an assistant."""

    def __init__(self):
        self._value_map: dict[AssistantStepEnumType, AssistantStepType] = dict(
            [(entry.value, entry) for entry in self.get_step_definitions()]
        )

    def get_step_definitions(self) -> list[AssistantStepType]:
        return self.step_definitions

    @property
    def step_list(self) -> list[AssistantStepType]:
        return self.get_step_definitions()

    def get_step(self, value: AssistantStepEnumType) -> AssistantStepType:
        return self._value_map[value]

    def get_page_name(self, value: AssistantStepEnumType) -> str:
        return self._value_map[value].page_name

    def get_label(self, value: AssistantStepEnumType) -> str:
        return self._value_map[value].label
