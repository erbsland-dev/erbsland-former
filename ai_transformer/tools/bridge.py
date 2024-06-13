#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC, abstractmethod
from typing import Optional

from ai_transformer.tools.chat_messages import AiChatMessages
from ai_transformer.tools.chat_response import AiChatResponse
from ai_transformer.tools.model_info import ModelInfo
from ai_transformer.transformer.profile_settings import AiProfileSettings
from ai_transformer.transformer.user_settings import AiUserSettings
from tasks.tools.log_level import LogLevel
from tasks.tools.log_receiver import LogReceiver


class Bridge(LogReceiver, ABC):

    def __init__(self):
        self._log: Optional[LogReceiver] = None
        self._model: Optional[ModelInfo] = None

    def set_log_receiver(self, log: LogReceiver) -> None:
        self._log = log

    def log_message(self, level: LogLevel, message: str, details: str = None) -> None:
        self._log.log_message(level, message, details)

    def set_model_info(self, model_info: ModelInfo) -> None:
        self._model = model_info

    @property
    def model(self) -> ModelInfo:
        return self._model

    @abstractmethod
    def setup(self, user_settings: AiUserSettings, profile_settings: AiProfileSettings) -> None:
        """
        Setup this bride, using parameters from the user settings (or other sources).

        :param user_settings: The user settings object from the current user.
        :param profile_settings: The profile settings.
        :raises TransformerError: If there is a problem with the settings.
        """
        pass

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the bridge.

        This method is called after `setup`. It must verify that the settings provided with the `setup` call are
        correct, and e.g. a connection to the backend is possible.

        :raises TransformerError: If there is a problem with the settings.
        """
        pass

    @abstractmethod
    def request_completion(self, messages: AiChatMessages) -> AiChatResponse:
        """
        Make a completion request to the model, using the prepared message list.

        In case of any technical problem (limits, access, etc.), this method shall raise a TransformerError and
        not return a chat response.

        :param messages: The prepared message list.
        :return: A valid chat response that contains output from the model.
        :raises TransformerError: If there is a technical problem.
        """
        pass
