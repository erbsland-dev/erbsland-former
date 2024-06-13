#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from ai_transformer.tools.model_info import ModelInfo
from backend.size_calculator.base import SizeCalculatorBase


class AiModelSizeCalculatorBase(SizeCalculatorBase):
    """
    A size calculator based on the registered models in the model manager.
    """

    unit_name = _("Tokens")

    def __init__(self, model_info: ModelInfo):
        self._model_info = model_info

    def get_name(self) -> str:
        # Convert the identifier from the API into one suitable as extension name.
        name = self._model_info.identifier
        name = name.replace("-", "_").replace(".", "_")
        return f"token_{name}"

    def get_verbose_name(self) -> str:
        return _("Tokens for %(model_name)s") % {"model_name": self._model_info.verbose_name}

    def get_minimum_fragment_size_recommendation(self) -> int:
        return self._model_info.minimum_fragment_size

    def get_maximum_fragment_size_recommendation(self) -> int:
        return self._model_info.maximum_fragment_size

    def size_for_text(self, text: str) -> int:
        return self._model_info.get_token_count(text)
