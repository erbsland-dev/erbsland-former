#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any

from backend.transformer.context import TransformerFragmentContext, TransformerDocumentContext
from backend.transformer.result import ProcessorResult
from backend.transformer.settings import TransformerSettingsBase
from tasks.data_store import data_store
from tasks.tools.log_level import LogLevel
from tasks.tools.log_receiver import LogReceiver

UserSettings = TypeVar("UserSettings", bound=TransformerSettingsBase)
ProfileSettings = TypeVar("ProfileSettings", bound=TransformerSettingsBase)


class Processor(LogReceiver, Generic[ProfileSettings, UserSettings]):
    """
    The processor part of a transformer.

    A new instance of the processor is created for each transformation. This instance is used to process the
    selected content of a project. Each document fragment is fed into the `transform` method in the
    *ordered sequence* as they are selected by the user.

    For this reason, it is safe if you like to keep a history of processed data, e.g. to make sure the
    transition between two fragments is transformed correctly. You can also use `context` to access previous
    processed fragments, or the previous or next fragments in the current processed document.

    The transformation is run in a separate process and can block processing for a long time. Yet, you should
    check the method `is_stop_requested` in regular intervals to make sure the transformation can be stopped
    on user request.
    """

    def __init__(
        self,
        task_id: str,
        log_receiver: LogReceiver,
        profile_settings: ProfileSettings,
        user_settings: Optional[UserSettings] = None,
    ):
        """
        Create a new instance of the processor.

        :param task_id: The task ID that is assigned to the running transformation.
        :param log_receiver: The log_receiver instance that is used to log messages.
        :param profile_settings: The profile settings for the transformation.
        :param user_settings: The optional user settings for this transformer.
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string.")
        if not isinstance(profile_settings, TransformerSettingsBase):
            raise TypeError("profile_settings must be a object derived from TransformerSettingsBase.")
        if not (user_settings is None or isinstance(user_settings, TransformerSettingsBase)):
            raise TypeError("user_settings must be a object derived from TransformerSettingsBase.")
        self.task_id: str = task_id
        self._log_receiver: LogReceiver = log_receiver
        self.profile_settings: ProfileSettings = profile_settings
        self.user_settings: UserSettings = user_settings

    def log_message(self, level: LogLevel, message: str, details: str = None) -> None:
        self._log_receiver.log_message(level, message, details)

    def initialize(self):
        """
        This method is called once, just after the processor is created to allow any initializations that have
        to be done before content can be transformed. Use it to prepare data structures that speed up the processing.

        Any exception thrown by this method will prevent any transformations done.
        """
        pass

    def shut_down(self):
        """
        This method is called when all work is done or the user stopped the transformation, but not if the processor
        raised an exception in one of its methods. Use it to free resources, close connections or delete temporary
        files.

        Note:
            This method should not throw any exceptions, and handle errors internally.
        """

    def document_begin(self, context: TransformerDocumentContext) -> None:
        """
        This method is called before the first fragment in a document is processed.

        Note:
            This method should not throw any exceptions, and handle errors internally.

        :param context: The document context.
        """
        pass

    def document_end(self, context: TransformerDocumentContext) -> None:
        """
        This method is called after the last fragment in a document is processed.

        Note:
            This method should not throw any exceptions, and handle errors internally.

        :param context: The document context.
        """
        pass

    @abstractmethod
    def transform(self, content: str, context: TransformerFragmentContext) -> ProcessorResult:
        """
        Transform content.

        Transforms the passed content and returns the result of that operation.
        Output can optionally be provided in success case, but must be provided in an error case.

        Instead of returning a result with an error, you can also throw a `TransformerError` exception. This
        will automatically create an error result with empty content and the exception as output.

        In case a transformation takes a long time, use the method `is_stop_requested` to check every few
        seconds if the user requested to stop (abort) the operation. For transformations that take less than
        20 seconds, there is usually no need to do that.

        Note:
            This method should not throw any exceptions, and handle errors internally. If there are errors during the
            transformation, write them into the error field in the `ProcessorResult` object.

        :param content: The content to transform.
        :param context: The context with all context-information about the content.
        :return: The result of the transformation.
        """
        pass

    @property
    def is_stop_requested(self) -> bool:
        """
        Test if the user chose to stop the current processing.
        """
        is_stop, _ = data_store.get_task_stop_request(self.task_id)
        return is_stop

    def get_statistics(self) -> dict[str, Any]:
        """
        Return additional stats about the transformation to be stored in the transformer and for the
        "done" page at the end and to be stored in the transformation history.
        """
        return {}

    def get_status_values(self) -> dict[str, str]:
        """
        Return additional status values to be displayed while the processor is running.
        This method is called after every `transform` call.
        """
        return {}
