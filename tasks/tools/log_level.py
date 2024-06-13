#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import enum
import logging


class LogLevel(enum.StrEnum):
    """
    The log level for action messages.
    """

    INFO = "info"
    """Informal message that indicate important phases of a process."""

    WARNING = "warning"
    """Warnings about problems that potentially could cause unexpected results."""

    ERROR = "error"
    """Errors, that lead to failed actions or problems."""

    DEBUG = "debug"
    """Messages only written into the log that have a use while developing an application."""

    def to_logger_level(self) -> int:
        """
        Translate this log level into a logging level of the `logger` library.
        """
        match self:
            case LogLevel.INFO:
                return logging.INFO
            case LogLevel.WARNING:
                return logging.WARNING
            case LogLevel.ERROR:
                return logging.ERROR
            case LogLevel.DEBUG:
                return logging.DEBUG
