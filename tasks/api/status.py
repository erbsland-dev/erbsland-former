#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import logging
from datetime import timedelta, datetime, UTC
from typing import Optional

import humanize
from django.core.exceptions import BadRequest
from django.db import transaction
from django.http import Http404, HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from tasks.api.base import ApiHandler
from tasks.api.error import ValidationError
from tasks.data_store import data_store, DataStatus
from tasks.models import TaskStatus, TaskResult
from tasks.models.task import Task


class StatusHandler(ApiHandler):
    """
    Handler for status requests.
    """

    action = "status"

    def __init__(self, request: HttpRequest, logger: logging.Logger):
        super().__init__(request, logger)
        self.data_status: Optional[DataStatus] = None
        self.task_id: Optional[str] = None
        self.task: Optional[Task] = None

    def handle(self, task_id: str, data: dict) -> dict:
        self.task_id = task_id
        self.data_status = data_store.get_task_status(task_id)
        if not self.data_status:
            raise ValidationError("No task with this ID.")
        try:
            if self.data_status.stop_requested:
                self._handle_stop()
        except BadRequest as e:
            self.data_status = self._bad_request_data(e)
        return self.data_status.to_json()

    @staticmethod
    def _bad_request_data(e: Exception) -> DataStatus:
        return DataStatus(
            time=datetime.now(UTC),
            status=TaskStatus.FINISHED,
            result=TaskResult.FAILURE,
            progress=100.0,
            status_values={},
            text=_("Internal error: %(error)s") % {"error": str(e)},
            next_url=reverse("home"),
        )

    def _get_task(self) -> None:
        """
        Get the task object.
        """
        try:
            self.task = Task.objects.get(pk=self.task_id)
        except Task.DoesNotExist:
            raise BadRequest(_("This task no longer exists"))

    def _handle_stop(self) -> None:
        """
        Handle the case when the task is stopped.
        """
        # Investigate the current state in more detail.
        with transaction.atomic():
            self._get_task()
            if self.task.owner != self.request.user:
                raise BadRequest(_("You have no access to this task"))
            if self.task.status == TaskStatus.FINISHED:
                return  # The task has already finished, no need to stop it anymore.
            if not self.task.stop_requested:
                return self._handle_race_conditions()
            if (datetime.now(UTC) - self.data_status.time) > timedelta(minutes=5):
                return self._handle_unresponsive()

    def _handle_unresponsive(self):
        # If stop was requested, and a task is unresponsive for more than five minutes,
        # consider it as crashed or hung up. It should be safe to force the task into stopped state.
        self.task.task_status = TaskStatus.FINISHED
        self.task.task_result = TaskResult.STOPPED
        self.task.save()
        text = _("The task was forcefully stopped, after it was not responsive for more than five minutes.")
        data_store.set_task_finished(
            self.task_id,
            TaskResult.STOPPED,
            {},
            text,
            next_url=self.task.stopped_url,
        )
        self.data_status = DataStatus(
            time=datetime.now(UTC),
            status=TaskStatus.FINISHED,
            result=TaskResult.STOPPED,
            progress=100.0,
            status_values={},
            text=text,
            next_url=reverse("home"),
        )

    def _handle_race_conditions(self) -> None:
        # That's tricky, most likely a race condition. Therefore, ignore it.
        # In case of data corruption, the user can hit the stop button again.
        if (datetime.now(UTC) - self.data_status.time) < timedelta(seconds=10):
            self.data_status.stop_requested = False
            return
        # If the request is older than 10 seconds, and the db wasn't updated yet,
        # remove the stop signal, so the user can request stop again.
        data_store.set_task_stop_request(self.task_id, False)
        self.data_status.stop_requested = False
