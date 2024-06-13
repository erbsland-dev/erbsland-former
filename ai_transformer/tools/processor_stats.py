#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from ai_transformer.tools.chat_response import AiChatResponse
from ai_transformer.tools.constants import (
    STATUS_TOTAL_TOKENS,
    STATUS_TOTAL_COST,
    STATISTIC_COMPLETION_TOKENS,
    STATISTIC_PROMPT_TOKENS,
    STATISTIC_TOTAL_TOKENS,
    STATISTIC_TOTAL_COST,
    STATISTIC_CURRENCY,
)
from ai_transformer.tools.model_info import ModelInfo


class AiProcessorStats:
    """Stats to be stored for the transformation."""

    def __init__(self):
        self.output_tokens: int = 0
        self.input_tokens: int = 0
        self.total_tokens: int = 0
        self.currency: str = "USD"

    def get_total_cost(self, model_info: ModelInfo) -> float:
        return (
            self.input_tokens * model_info.price_input / 1_000_000.0
            + self.output_tokens * model_info.price_output / 1_000_000.0
        )

    def to_status(self, model_info: ModelInfo) -> dict[str, Any]:
        return {
            STATUS_TOTAL_TOKENS: f"{self.total_tokens} Tokens",
            STATUS_TOTAL_COST: f"{self.get_total_cost(model_info):0.2f} {self.currency}",
        }

    def to_statistic(self, model_info: ModelInfo) -> dict[str, Any]:
        return {
            STATISTIC_COMPLETION_TOKENS: f"{self.output_tokens} Tokens",
            STATISTIC_PROMPT_TOKENS: f"{self.input_tokens} Tokens",
            STATISTIC_TOTAL_TOKENS: f"{self.total_tokens} Tokens",
            STATISTIC_TOTAL_COST: f"{self.get_total_cost(model_info):0.2f} {self.currency}",
            STATISTIC_CURRENCY: self.currency,
        }

    def add_response(self, response: AiChatResponse):
        self.input_tokens += response.input_tokens
        self.output_tokens += response.output_tokens
        self.total_tokens += response.total_tokens
