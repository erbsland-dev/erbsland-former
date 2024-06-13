#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from dataclasses import dataclass, field
from datetime import timedelta
from functools import partial, cached_property
from typing import Optional

from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

from tasks.actions.status import TaskStatusField
from tasks.data_store import data_store
from tasks.models.task_result import TaskResult
from tasks.models.task_runner import TaskRunner
from tasks.models.task_status import TaskStatus


@dataclass(frozen=True)
class TaskParameter:
    task_runner: TaskRunner
    """The object that is running a task."""
    user: User
    """The user started this task."""
    action: str
    """The name of the action to perform."""
    input_data: dict
    """A JSON compatible dictionary with the input data for the task."""
    success_url: str = ""
    """The URL to go if the action is successfully executed."""
    failure_url: str = ""
    """The URL to go if the action failed."""
    stopped_url: str = ""
    """The URL to go if the user stopped the action."""
    additional_status_fields: Optional[list[TaskStatusField]] = field(default_factory=list)
    """A list of additional status fields to add to the task."""
    language_code: Optional[str] = None
    """The optional language code. If you omit it, the language code is
    automatically retrieved using Django's `translation.get_language()`."""


class TaskManager(models.Manager):
    """
    The task manager.
    """

    def start_task(self, param: TaskParameter) -> "Task":
        """
        Start a task.

        **You must call this method inside an atomic operation.**

        The `run_task_action()` is started when the transaction is committed.
        For extra safety, the task is waiting up to 10 seconds for the task object to appear if it does not
        exist at the start.

        :param param: The task parameters.
        :return: The new task object.
        """
        from tasks.tasks import run_task_action
        from tasks.actions import action_manager

        # only create a task if there is not already one running.
        if param.task_runner.has_unfinished_tasks():
            raise ValueError("There are unfinished tasks.")
        status_fields = action_manager.get_status_fields(param.action)
        if param.additional_status_fields:
            status_fields.extend(param.additional_status_fields)
        status_fields_json = [status_field.to_json() for status_field in status_fields]
        language_code = param.language_code
        if not param.language_code:
            language_code = translation.get_language()
        task = self.create(
            task_runner=param.task_runner,
            owner=param.user,
            action=param.action,
            success_url=param.success_url,
            failure_url=param.failure_url,
            stopped_url=param.stopped_url,
            input_data=param.input_data,
            status_fields=status_fields_json,
            language_code=language_code,
        )
        # Initialize the status in the broker to allow a dynamic status, even the background process fails to start.
        data_store.create_task_status(str(task.pk))
        # At this point, the task object should be accessible by the backend process.
        # Only start the backend task after all database operations were successfully committed.
        transaction.on_commit(partial(run_task_action.delay, str(task.pk)))
        return task

    def clean_up(self):
        """
        Clean-up tasks that are finished and are older than 5 minutes.
        """
        with transaction.atomic():
            time_threshold = timezone.now() - timedelta(minutes=5)
            tasks = self.filter(status=TaskStatus.FINISHED, modified__lt=time_threshold)
            for task in tasks:
                task.delete()
                data_store.del_all_task_data(str(task.pk))


class Task(models.Model):
    """
    A task running in the background.

    The task object serves many purposes: First, it provides the unique id for the task that is also used in Redis for
    the "real time" communication between the task and the interface. It also holds the name and main status of the
    task, its input and output data in JSON format. Creation and modified time allow purging tasks that were
    abandoned, e.g. because the backend task queue was stopped and the database got out of sync.

    Tasks in finished state may linger in the database for a while, until they are cleaned when the user
    reviewed the results or performs any other action on a project.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """A unique ID for the task."""

    task_runner = models.ForeignKey(TaskRunner, on_delete=models.RESTRICT, related_name="tasks")
    """The project for the task."""

    owner = models.ForeignKey(User, on_delete=models.RESTRICT)
    """The user that started this task."""

    action = models.CharField(max_length=32)
    """The name of the action this task performs."""

    language_code = models.CharField(max_length=32)
    """The language code from the frontend to render translated messages in the backend correctly."""

    success_url = models.CharField(max_length=250, blank=True, default="")
    """The URL to display for successful tasks that are part of an assistant like interface."""

    failure_url = models.CharField(max_length=250, blank=True, default="")
    """The URL to display for failed tasks that are part of an assistant like interface."""

    stopped_url = models.CharField(max_length=250, blank=True, default="")
    """The URL to display for stopped tasks that are part of an assistant like interface."""

    status = models.SmallIntegerField(choices=TaskStatus.choices, default=TaskStatus.CREATED.value)
    """The status of the task."""

    result = models.SmallIntegerField(choices=TaskResult.choices, default=TaskResult.NONE.value)
    """The result of the task."""

    input_data = models.JSONField()
    """The input for this task."""

    status_fields = models.JSONField()
    """The status fields of this task."""

    output_data = models.JSONField(null=True)
    """The output for this task."""

    stop_requested = models.BooleanField(default=False)
    """If the user requested to stop this task (in the frontend)."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the task was created."""

    modified = models.DateTimeField(auto_now=True)
    """The date when the task was last modified."""

    objects = TaskManager()
    """The task manager."""

    @property
    def task_result(self) -> TaskResult:
        return TaskResult(self.result)

    @task_result.setter
    def task_result(self, value: TaskResult):
        if not isinstance(value, TaskResult):
            raise TypeError(f"TaskResult must be of type TaskResult, got {type(value)}")
        self.result = value.value

    @property
    def task_status(self) -> TaskStatus:
        return TaskStatus(self.status)

    @task_status.setter
    def task_status(self, value: TaskStatus) -> None:
        if not isinstance(value, TaskStatus):
            raise TypeError(f"TaskStatus must be of type TaskStatus, got {type(value)}")
        self.status = value.value

    def get_next_url(self) -> str:
        """
        Get the next url if the task has finished.
        """
        result = self.task_result
        match result:
            case TaskResult.SUCCESS:
                return self.success_url
            case TaskResult.FAILURE:
                return self.failure_url
            case TaskResult.STOPPED:
                return self.stopped_url
        return ""

    def get_progress_title(self) -> str:
        """
        Get the title for this task for status displays.
        """
        from tasks.actions.manager import action_manager

        return action_manager.get_progress_title(self.action)

    def get_progress_subject(self) -> str:
        """
        Get the subject of this task for
        """
        from tasks.actions.manager import action_manager

        return action_manager.get_progress_subject(self.action)

    @cached_property
    def status_field_list(self) -> list[TaskStatusField]:
        if not isinstance(self.status_fields, list):
            return []
        return list(TaskStatusField.from_json(entry) for entry in self.status_fields)

    def get_status_field_column_count(self) -> int:
        """
        Get the number of columns for the status fields.
        """
        if len(self.status_field_list) > 8:
            return 2
        return 1

    def get_status_field_columns(self) -> list[list[TaskStatusField]]:
        """
        Get the status fields for this task
        """
        if self.get_status_field_column_count() == 1:
            return [self.status_field_list]
        midpoint = len(self.status_field_list) // 2 + 1
        return [
            self.status_field_list[:midpoint],
            self.status_field_list[midpoint:],
        ]

    def set_status_fields(self, status_fields: list[TaskStatusField]) -> None:
        """
        Set the status fields for this task.

        :param status_fields: The list of status fields to set.
        """
        if not isinstance(status_fields, list):
            raise TypeError(f"Status fields must be of type list, got {type(status_fields)}")
        self.status_fields = [field.to_json() for field in status_fields]
        # clear the cache.
        if hasattr(self, "status_field_list"):
            delattr(self, "status_field_list")

    def __str__(self) -> str:
        return (
            f"pk={self.pk}, action={self.action}, status={self.task_status.name} "
            f"result={self.task_result.name} next_url={self.get_next_url()}"
        )

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        indexes = [
            models.Index(fields=["task_runner"], name="task_task_runner_idx"),
            models.Index(fields=["owner"], name="task_owner_idx"),
            models.Index(fields=["status"], name="task_status_idx"),
        ]
