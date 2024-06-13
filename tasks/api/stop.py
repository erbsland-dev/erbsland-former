#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import PermissionDenied
from django.db import transaction

from tasks.api.base import ApiHandler
from tasks.data_store import data_store
from tasks.models import Task


class StopHandler(ApiHandler):
    """
    Handler for stop requests.
    """

    action = "stop"

    def handle(self, task_id: str, data: dict) -> dict:
        self.logger.warning(f"User requested to stop task {task_id}")
        with transaction.atomic():
            try:
                task = Task.objects.get(pk=task_id)
            except Task.DoesNotExist:
                self.logger.warning(f"The requested task does not exist.")
                raise PermissionDenied("You have no access to this task.")
            if task.owner != self.request.user:
                self.logger.warning(f"The user tried to stop a task that it does not own.")
                raise PermissionDenied("You have no access to this task.")
            task.stop_requested = True
            task.save()
        data_store.set_task_stop_request(task_id, True)
        data = {"status": "stopping"}
        return data
