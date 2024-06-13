#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod

from tasks.tools.log_level import LogLevel


class LogReceiver(ABC):
    """
    A log receiver.
    """

    @abstractmethod
    def log_message(self, level: LogLevel, message: str, details: str = None) -> None:
        """
        Write an informal message to the log.

        This message is written in the backend log and is also visible in the frontend.

        :param level: The log level.
        :param message: A log message, ideally fitting into a single line.
        :param details: The details of the message that are displayed on request.
        """
        pass

    def log_info(self, message: str, details: str = None) -> None:
        """
        Write an informal message to the log.

        This message is written in the backend log and is also visible in the frontend.

        :param message: A log message, ideally fitting into a single line.
        :param details: The details of the message that are displayed on request.
        """
        self.log_message(LogLevel.INFO, message, details)

    def log_warning(self, message: str, details: str = None):
        """
        Write a warning message to the log.

        This message is written in the backend log and is also visible in the frontend.

        :param message: A log message, ideally fitting into a single line.
        :param details: The details of the message that are displayed on request.
        """
        self.log_message(LogLevel.WARNING, message, details)

    def log_error(self, message: str, details: str = None):
        """
        Write an error message to the log.

        This message is written in the backend log and is also visible in the frontend.

        :param message: A log message, ideally fitting into a single line.
        :param details: The details of the message that are displayed on request.
        """
        self.log_message(LogLevel.ERROR, message, details)

    def log_debug(self, message: str, details: str = None):
        """
        Write a debugging message to the log.

        This message is only written into the backend log and is not visible in the frontend.

        :param message: A log message, ideally fitting into a single line.
        :param details: The details of the message that are displayed on request.
        """
        self.log_message(LogLevel.DEBUG, message, details)
