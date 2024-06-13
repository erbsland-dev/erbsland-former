#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property

from ai_transformer.tools.chat_message_role import AiChatMessageRole
from ai_transformer.tools.model_info import ModelInfo


class AiChatMessage:
    """One entry in the chat."""

    def __init__(self, model: ModelInfo, role: AiChatMessageRole, content: str, is_prompt: bool = False):
        """
        Create a new entry.

        :param role: The role: "system", "user", "assistant".
        :param content: The content.
        """
        if not isinstance(model, ModelInfo):
            raise TypeError("model must be a ModelInfo")
        if not isinstance(role, AiChatMessageRole):
            raise TypeError("role must be a AiChatMessageRole.")
        if not isinstance(content, str):
            raise TypeError("content must be a string.")
        self._model: ModelInfo = model
        self._role: AiChatMessageRole = role
        self._content: str = content
        self._is_prompt: bool = is_prompt

    @property
    def role(self) -> AiChatMessageRole:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    @property
    def is_prompt(self) -> bool:
        return self._is_prompt

    @cached_property
    def token_count(self) -> int:
        """Get the token count for the content of this entry."""
        result = self._model.tokens_per_message
        for key, value in self.to_json().items():
            result += self._model.get_token_count(value)
            if key == "name":
                result += self._model.tokens_per_name
        return result

    def to_json(self) -> dict[str, str]:
        """Convert this message into JSON."""
        return {
            "role": str(self._role),
            "content": self._content,
        }
