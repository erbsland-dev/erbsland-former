#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import copy
from typing import Optional

from ai_transformer.tools.chat_history import AiChatHistory
from ai_transformer.tools.chat_message import AiChatMessage
from ai_transformer.tools.chat_message_role import AiChatMessageRole
from ai_transformer.tools.model_info import ModelInfo


class AiChatMessages:
    """A full request."""

    def __init__(self, model: ModelInfo, maximum_request_size: int):
        """
        Create a new chat message list.

        :param model: The used model.
        :param maximum_request_size: The maximum request size.
        """
        self._model: ModelInfo = model
        self._maximum_request_size: int = maximum_request_size
        self._messages: list[AiChatMessage] = []

    @property
    def maximum_request_size(self) -> int:
        return self._maximum_request_size

    def set_system_message(self, content: str) -> None:
        """
        Set the system message.

        :param content: The content of the system message.
        """
        if self.has_system_message:
            raise ValueError("There is already a system message in this list.")
        self._messages.insert(0, AiChatMessage(self._model, AiChatMessageRole.SYSTEM, content))

    @property
    def has_system_message(self) -> bool:
        return self._messages and self._messages[0].role == "system"

    def set_user_prompt(self, content: str) -> None:
        if self._messages and self._messages[-1].is_prompt:
            raise ValueError("There is already a user prompt in this list.")
        self._messages.append(AiChatMessage(self._model, AiChatMessageRole.USER, content, is_prompt=True))

    def fill_chat_history(self, history: AiChatHistory) -> None:
        """
        Fill this message list with chat history.

        :param history: The chat history database.
        """
        for message in history.messages:
            if (self.token_count + message.token_count) >= self._maximum_request_size:
                break
            self._messages.insert(1 if self.has_system_message else 0, message)

    @property
    def messages(self) -> list[AiChatMessage]:
        return self._messages

    @property
    def token_count(self) -> int:
        """
        Get the total token count for this message list.
        """
        result = self._model.tokens_per_request
        for message in self._messages:
            result += message.token_count
        return result

    @property
    def user_prompt(self) -> str:
        """
        Get the last user prompt from this message list.
        """
        if not self._messages:
            return ""
        if self._messages[-1].role != AiChatMessageRole.USER:
            return ""
        return self._messages[-1].content

    def create_followup(self, model_response: str, user_prompt: str):
        """
        Create a followup based on this message list.

        This adds the response from the model as new "assistant" message and adds a new user prompt.
        The function makes sure that the total request size does not exceed `maximum_request_size`.

        :param model_response: The raw response from the model.
        :param user_prompt: The new user prompt for the followup.
        :return: A new copy of the message list with the added followup.
        """
        result = self.copy()
        result.add_followup(model_response, user_prompt)
        return result

    def add_followup(self, model_response: str, user_prompt: str) -> None:
        """
        Add a followup to this message.

        :param model_response: The raw response from the model.
        :param user_prompt: The new user prompt for the followup.
        """
        self._messages.append(AiChatMessage(self._model, AiChatMessageRole.ASSISTANT, model_response))
        self._messages.append(AiChatMessage(self._model, AiChatMessageRole.USER, user_prompt))
        minimum_message_count = 2
        if self.has_system_message:
            minimum_message_count += 3
        # Remove messages until it fits into the request size.
        while len(self._messages) > minimum_message_count and self.token_count > self._maximum_request_size:
            del self._messages[1 if self.has_system_message else 0]

    def copy(self):
        result = type(self)(self._model, self._maximum_request_size)
        result._messages = self._messages.copy()
        return result

    def to_json(self):
        """
        Convert this into JSON for a request.
        """
        return list(entry.to_json() for entry in self._messages)
