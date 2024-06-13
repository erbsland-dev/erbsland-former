#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import json
from pathlib import Path
from typing import Union

from django.utils.functional import LazyObject
from django.utils.translation import gettext_lazy as _

from ai_transformer.tools.model_info import ModelInfo
from backend.transformer.error import TransformerError


class ModelManager:
    """The model manager that provides access to the model info of all supported models."""

    def __init__(self):
        self._model_list: list[ModelInfo] = []
        self._model_map: dict[str, ModelInfo] = {}
        self._load_models()

    def _load_models(self):
        json_file = Path(__file__).parent / "supported_models.json"
        with open(json_file, "r") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("The file `supported_models.json` is has no list as root element.")
        for model_data in data:
            model_info = ModelInfo(model_data)
            self._model_list.append(model_info)
            self._model_map[model_info.identifier] = model_info

    def get_model_list(self) -> list[ModelInfo]:
        return self._model_list

    def get_model(self, identifier: str) -> ModelInfo:
        if identifier not in self._model_map:
            raise TransformerError(
                _("The model '%(model_name)s' is not supported by this application.") % {"model_name": identifier}
            )
        return self._model_map.get(identifier)


class LazyModelManager(LazyObject):
    """
    A lazy object wrapper around the model manager.
    """

    def _setup(self):
        self._wrapped = ModelManager()


model_info_manager: Union[ModelManager, LazyModelManager] = LazyModelManager()
"""The global instance of the model manager."""
