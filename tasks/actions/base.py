#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime, UTC, timedelta
from typing import Optional

import humanize
from math import isclose
from django.utils.translation import gettext_lazy as _

from tasks.actions.exception import ActionStoppedByUser
from tasks.tools.log_receiver import LogReceiver
from tasks.actions.status import TaskStatusField
from tasks.actions.status_keys import (
    STATUS_NAME_COMPLETED,
    STATUS_NAME_STARTED,
    STATUS_NAME_RUNNING,
    STATUS_NAME_EST_DURATION,
    STATUS_NAME_EST_END,
)
from tasks.data_store import data_store, LogLevel


class ActionBaseMeta(ABCMeta):
    """
    The metaclass for all actions, making sure all required class fields are set.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        # Classes that have a `Base` are considered abstract and must not be compliant.
        if cls.__name__.endswith("Base"):
            return cls
        for class_variable in ["name", "progress_title", "progress_subject"]:
            value = namespace.get(class_variable, None)
            if not value:
                raise ValueError(f"You must provide a value for '{class_variable}' in class '{cls.__name__}'")
        return cls


class ActionBase(LogReceiver, metaclass=ActionBaseMeta):
    """
    This is the base class of all actions.

    Actions that are declared in the "actions" module of an application are automatically loaded when
    the manager instance is created.
    """

    name = None
    """You must set the name of the action, e.g. 'file_analysis'."""

    progress_title = None
    """A title that is displayed when this action is running, e.g. 'Analyzing files'."""

    progress_subject = None
    """The subject of the action, e.g. "Analysis" to build text like 'Stop analysis'."""

    status_fields = []
    """Additional status fields to be displayed for this action."""

    def __init__(self, task_id: str, log: logging.Logger):
        self.task_id = task_id
        self._log = log
        self._status_progress: float = 0.0
        self._status_text: str = "Working..."
        self._started_at: datetime = datetime.now(UTC)
        self._next_estimate: Optional[timedelta] = None
        self._last_estimates: list[timedelta] = []

    @classmethod
    def get_progress_title(cls) -> str:
        """Get the static title for the progress display."""
        return cls.progress_title

    @classmethod
    def get_progress_subject(cls) -> str:
        """Get the static subject for the progress display."""
        return cls.progress_subject

    @classmethod
    def get_status_fields(cls) -> list[TaskStatusField]:
        """Get the list of status fields to be displayed for this action."""
        status_fields: list[TaskStatusField] = [
            TaskStatusField(STATUS_NAME_COMPLETED, _("Completed"), "—", "list-check"),
            TaskStatusField(STATUS_NAME_STARTED, _("Started"), "—", "hourglass-start"),
            TaskStatusField(STATUS_NAME_RUNNING, _("Running for"), "—", "stopwatch"),
            TaskStatusField(STATUS_NAME_EST_DURATION, _("Estimated Duration"), "—", "clock"),
            TaskStatusField(STATUS_NAME_EST_END, _("Estimated End"), "—", "flag-checkered"),
        ]
        status_fields.extend(cls.status_fields)
        return status_fields

    def check_if_stop_requested(self) -> None:
        """
        Check if a stop request has been made for the current task.

        :raises: ActionStopped if a stop request has been made
        """
        should_stop, _ = data_store.get_task_stop_request(self.task_id)
        if should_stop:
            raise ActionStoppedByUser()

    def set_progress(self, current_step: float, total_steps: float, text="", status_values: dict[str, str] = None):
        """
        Set the progress counter in percent.

        This method also checks if the user requested a stop of the current action.

        :param current_step: The index of the current step.
        :param total_steps: The number of total steps.
        :param text: The text that describes the current process.
        :param status_values: Additional status values for the declared status fields.
        :raises: ActionStopped if a stop request has been made
        """
        # Only update the db if there is an actual change.
        self.check_if_stop_requested()
        progress = round(current_step / total_steps * 100, 2)
        if isclose(self._status_progress, progress) and self._status_text == text:
            return
        self._status_progress = progress
        self._status_text = text
        if not status_values:
            status_values = {}
        passed_time = datetime.now(UTC) - self._started_at
        status_values[STATUS_NAME_COMPLETED] = f"{progress:0.2f}%"
        status_values[STATUS_NAME_STARTED] = humanize.naturaltime(self._started_at)
        if passed_time.total_seconds() >= 10 and progress >= 1.0:
            if self._next_estimate is None or passed_time > self._next_estimate:
                estimated_duration = passed_time / (current_step / total_steps)
                self._last_estimates.append(estimated_duration)
                if len(self._last_estimates) > 10:
                    self._last_estimates.pop(0)
                self._next_estimate = passed_time + timedelta(seconds=1)
            avg_duration = sum(self._last_estimates, timedelta()) / len(self._last_estimates)
            estimated_end = self._started_at + avg_duration
            status_values[STATUS_NAME_RUNNING] = humanize.naturaldelta(passed_time)
            status_values[STATUS_NAME_EST_DURATION] = humanize.naturaldelta(avg_duration)
            status_values[STATUS_NAME_EST_END] = humanize.naturaltime(estimated_end)
        data_store.update_task_progress(self.task_id, self._status_progress, status_values, self._status_text)

    def log_message(self, level: LogLevel, message: str, details: str = None) -> None:
        if level != LogLevel.DEBUG:
            data_store.write_log(self.task_id, level, message, details or "")
        if details:
            message = f"{message} | Details: {details}"
        self._log.log(level.to_logger_level(), message)

    @abstractmethod
    def run(self, input_data: dict) -> None:
        """
        The code that is executed for this action.

        You must implement this method. If your code takes more than a few seconds, make sure to call
        `check_if_stop_requested()` in regular intervals (1-2 seconds). If the user requests a stop, this
        method raises an `ActionStoppedByUser` exception. You can handle this exception to do clean-up and
        restore the original state.

        In case of any unrecoverable error, throw an `ActionError` exception with a message for the frontend and
        optional technical details for the log.

        Call the `log_info()`, `log_warning()`, `log_error()` and `log_debug()` methods to write messages to the
        log. The first three log message types are also transported to the frontend and can be seen by the user.

        :param input_data: The input data passed to this action.
        :raises ActionError: If an unrecoverable error happens.
        :raises ActionStoppedByUser: If the user stopped the action.
        """
        pass

    def get_output_data(self) -> dict:
        """
        Overwrite this method to return the output of this task.

        :return: A JSON compatible dictionary with the results of this task.
        """
        return {}

    def on_failed(self, error: Exception) -> None:
        """
        Overwrite this method to clean-up when the action has failed.

        ⚠️ Exceptions from this call are only logged, but ignored.

        :param error: The exception that caused the failure.
        """
        pass

    def on_stopped(self) -> None:
        """
        Overwrite this method to clean-up when the action was stopped.

        ⚠️ Exceptions from this call are only logged, but ignored.
        """
        pass
