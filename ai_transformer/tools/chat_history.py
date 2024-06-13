#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Generator

from ai_transformer.tools.chat_message import AiChatMessage
from ai_transformer.tools.chat_response import AiChatResponse
from ai_transformer.tools.model_info import ModelInfo


class AiChatHistory:
    """A chat history, managing previous messages, limit storage to a reasonable size."""

    MAXIMUM_CHAT_HISTORY_LENGTH = 100
    MINIMUM_CHAT_HISTORY_LENGTH = 10

    def __init__(self, model: ModelInfo):
        self._model = model
        self._messages: list[AiChatMessage] = []

    def add(self, message: AiChatMessage) -> None:
        self._messages.append(message)
        if len(self._messages) < self.MINIMUM_CHAT_HISTORY_LENGTH:
            return
        while self.token_count > (self._model.context_window + self._model.tokens_safety_margin):
            del self._messages[0]
        while len(self._messages) > self.MAXIMUM_CHAT_HISTORY_LENGTH:
            del self._messages[0]

    def add_response(self, response: AiChatResponse) -> None:
        for message in response.messages:
            self.add(message)

    @property
    def token_count(self) -> int:
        result = 0
        for message in self._messages:
            result += self._model.tokens_per_message
            result += message.token_count
        return result

    @property
    def messages(self) -> Generator[AiChatMessage, None, None]:
        """The messages, from new to old."""
        for msg in reversed(self._messages):
            yield msg
