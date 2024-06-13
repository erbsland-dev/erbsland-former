#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property
from typing import TypeVar, Type

import tiktoken
from django.utils.translation import gettext_lazy as _

from backend.transformer.error import TransformerError

T = TypeVar("T")


class ModelInfo:
    """
    Information about a language model.
    """

    def __init__(self, data: dict[str, str]):
        self._identifier: str = self._get_value(data, "identifier", str)
        self._verbose_name: str = self._get_value(data, "verbose_name", str)
        self._context_window: int = self._get_value(data, "context_window", int)
        self._tokens_per_request: int = self._get_value(data, "tokens_per_request", int)
        self._tokens_per_message: int = self._get_value(data, "tokens_per_message", int)
        self._tokens_per_name: int = self._get_value(data, "tokens_per_name", int)
        self._tokens_safety_margin: int = self._get_value(data, "tokens_safety_margin", int)
        self._maximum_output: int = self._get_value(data, "maximum_output", int)
        self._price_input: float = self._get_value(data, "price_input", float)
        self._price_output: float = self._get_value(data, "price_output", float)

    @staticmethod
    def _get_value(data: dict[str, str], key: str, expected_type: Type[T]) -> T:
        value = data.get(key)
        if not isinstance(value, expected_type):
            raise TypeError(f"Expected {key} to be of type {expected_type.__name__}, but got {type(value).__name__}")
        return value

    @property
    def identifier(self) -> str:
        """The identifier for the model used in the API."""
        return self._identifier

    @property
    def verbose_name(self) -> str:
        """A verbose name of the model displayed in the UI."""
        return self._verbose_name

    @property
    def context_window(self) -> int:
        """The number of supported tokens for the input context."""
        return self._context_window

    @property
    def tokens_per_request(self) -> int:
        """The number of tokens per request."""
        return self._tokens_per_request

    @property
    def tokens_per_message(self) -> int:
        """The number of tokens required per message."""
        return self._tokens_per_message

    @property
    def tokens_per_name(self) -> int:
        """The number of tokens per name."""
        return self._tokens_per_name

    @property
    def tokens_safety_margin(self) -> int:
        """A number of tokens added as safety margin."""
        return self._tokens_safety_margin

    @property
    def maximum_output(self) -> int:
        """The maximum number of output tokens."""
        return self._maximum_output

    @property
    def price_input(self) -> float:
        """The input pricing in USD per 1m tokens."""
        return self._price_input

    @property
    def price_output(self) -> float:
        """The output pricing in USD per 1m tokens."""
        return self._price_output

    @cached_property
    def minimum_fragment_size(self) -> int:
        """A recommendation for a minimum fragment size for this model."""
        return 200

    @cached_property
    def maximum_fragment_size(self) -> int:
        """A recommendation for a maximum fragment size for this model."""
        maximum_io = min(self.context_window, self.maximum_output)
        return maximum_io // 2

    @property
    def bridge_type(self) -> type:
        """The type of the bridge object to be used with this model."""
        # This is a placeholder to keep this code extensible.
        from ai_transformer.tools.openai_bridge import OpenAIBridge

        return OpenAIBridge

    @cached_property
    def token_encoding(self) -> tiktoken.Encoding:
        try:
            return tiktoken.encoding_for_model(self._identifier)
        except KeyError:
            raise TransformerError(_("The model '%(model_name)s' is not recognized by the tokenizer."))

    def create_bridge(self):
        """
        Create a new bridge instance for this model.
        """
        bridge_type = self.bridge_type
        return bridge_type()

    def get_token_count(self, text: str) -> int:
        """
        Calculate the token count for the given text.

        :param text: The text to get the token count for.
        :return: The token count.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string.")
        return len(self.token_encoding.encode(text))
