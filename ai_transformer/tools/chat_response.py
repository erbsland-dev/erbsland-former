#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from ai_transformer.tools.chat_message import AiChatMessage
from ai_transformer.tools.chat_message_role import AiChatMessageRole
from ai_transformer.tools.model_info import ModelInfo


class AiChatResponse:
    """
    The response to a completion request from the model.

    In the case multiple messages between the app and model are required to get a valid result,
    this whole conversation is recorded in this response - so it can be added to the chat history.
    """

    def __init__(self, model: ModelInfo):
        self._model = model
        self._messages: list[AiChatMessage] = []
        self._input_tokens: int = 0  # The tokens used for the input
        self._output_tokens: int = 0  # The tokens used for the output
        self._total_tokens: int = 0  # The total tokens

    def add_assistant_message(self, content: str) -> None:
        """
        Add "assistant" message with the output from the model.

        :param content: The raw model output.
        """
        self._messages.append(AiChatMessage(self._model, AiChatMessageRole.ASSISTANT, content))

    def add_user_message(self, content: str) -> None:
        """
        Add "user" message.

        :param content: The content of the user message
        """
        self._messages.append(AiChatMessage(self._model, AiChatMessageRole.USER, content))

    @property
    def messages(self) -> list[AiChatMessage]:
        return self._messages

    @property
    def collected_input(self) -> str:
        """
        The collected input from this response.
        """
        result = ""
        for message in self._messages:
            if message.role == AiChatMessageRole.USER:
                result += message.content
            elif message.role == AiChatMessageRole.ASSISTANT:
                result += "(... model response ...)\n"
            if not result.endswith("\n"):
                result += "\n"
        return result

    @property
    def collected_output(self) -> str:
        return "".join(message.content for message in self._messages if message.role == AiChatMessageRole.ASSISTANT)

    def add_token_counts(self, input_tokens: int, output_tokens: int = None, total_tokens: int = None) -> None:
        """
        Set the token counts from the model API response.

        This token counts are only used for cost calculations and statistics. All there values
        are recorded separately. If you omit the total, it is calculated from input + output.

        :param input_tokens: The number of tokens used for the prompt (context window)
        :param output_tokens: The number of tokens used for the output.
        :param total_tokens: The total number of tokens.
        """
        self._input_tokens += input_tokens
        if output_tokens is not None:
            self._output_tokens += output_tokens
        if total_tokens is not None:
            self._total_tokens += total_tokens
        else:
            self._total_tokens += self._input_tokens + self._output_tokens

    @property
    def input_tokens(self) -> int:
        return self._input_tokens

    @property
    def output_tokens(self) -> int:
        return self._output_tokens

    @property
    def total_tokens(self) -> int:
        return self._total_tokens
