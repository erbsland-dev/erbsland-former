#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Union, Optional, Tuple

import redis
from django.core.signing import Signer, BadSignature
from django.utils.functional import LazyObject
from django.utils.translation import gettext

from tasks.models.task_result import TaskResult
from tasks.models.task_status import TaskStatus
from tasks.tools.log_level import LogLevel

logger = logging.getLogger(__name__)


@dataclass
class DataStatus:
    time: datetime
    status: TaskStatus
    result: TaskResult
    progress: float
    status_values: dict[str, str]
    text: str
    next_url: str
    stop_requested: bool = False
    stop_request_time: Optional[datetime] = None

    def to_json(self) -> dict:
        return {
            "time": self.time.isoformat(),
            "status": self.status.name.lower(),
            "result": self.result.name.lower(),
            "progress": f"{self.progress:0.2f}",
            "status_values": self.status_values,
            "text": str(self.text),
            "next_url": str(self.next_url),
            "stop_requested": self.stop_requested,
            "stop_request_time": self.stop_request_time.isoformat(),
        }


class DataStore:
    """
    The interface to access the redis service from the backend.

    This interface is used by backend tasks and also from the frontend.
    """

    KEY_PREFIX = "erbsland_dev.task"
    KEY_STATUS = "status"
    KEY_REQUEST_STOP = "request_stop"
    KEY_LOG = "log"

    def __init__(self):
        from django.conf import settings

        logger.debug(
            f"Create connection to redis using host={settings.TASKS_DATA_REDIS_HOST} "
            f"port={settings.TASKS_DATA_REDIS_PORT} db={settings.TASKS_DATA_REDIS_DB_NUM}"
        )
        self._redis = redis.Redis(
            host=settings.TASKS_DATA_REDIS_HOST,
            port=settings.TASKS_DATA_REDIS_PORT,
            db=settings.TASKS_DATA_REDIS_DB_NUM,
            decode_responses=True,
        )
        self._signer = Signer()

    def _get_task_key(self, task_id: str, name: str):
        return f"{self.KEY_PREFIX}.{task_id}.{name}"

    def create_task_status(self, task_id: str) -> None:
        """
        Create the initial task status.

        Put it into the `created` state with progress 0 and set a task stop request to `False`.

        :param task_id: The task ID
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        self._redis.hset(
            self._get_task_key(task_id, self.KEY_STATUS),
            mapping={
                "time": datetime.now(UTC).isoformat(),
                "status": TaskStatus.CREATED.name,
                "result": TaskResult.NONE.name,
                "progress": "0",
                "status_values": "",
                "text": gettext("Queued, waiting for start ..."),
                "next_url": "",
            },
        )
        self.set_task_stop_request(task_id, False)

    def update_task_progress(self, task_id: str, progress: float, status_values: dict[str, str], text: str) -> None:
        """
        Update the progress of a task.

        :param task_id: The task ID
        :param progress: The progress in percent 0.0 - 100.0
        :param status_values: The values to display below the progress bar.
        :param text: A text describing what the task is working on.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        if not isinstance(progress, float):
            raise TypeError(f"progress must be float, not {type(progress)}")
        if not isinstance(status_values, dict):
            raise TypeError(f"status_values must be dict, not {type(status_values)}")
        if not isinstance(text, str):
            text = str(text)  # Force translated texts.
        self._redis.hset(
            self._get_task_key(task_id, self.KEY_STATUS),
            mapping={
                "time": datetime.now(UTC).isoformat(),
                "status": TaskStatus.RUNNING.name,
                "result": TaskResult.NONE.name,
                "progress": f"{progress:0.2f}",
                "status_values": json.dumps(status_values),
                "text": text,
                "next_url": "",
            },
        )

    def set_task_finished(
        self, task_id: str, result: TaskResult, status_values: dict[str, str], text: str, next_url: str
    ):
        """
        Set the finished state for a task.

        :param task_id: The task ID
        :param result: The result of the task
        :param text: A text describing the final result.
        :param status_values: The values to display below the progress bar.
        :param next_url: An optional URL where to go next.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        if not isinstance(result, TaskResult):
            raise TypeError(f"result must be TaskResult, not {type(result)}")
        if not isinstance(status_values, dict):
            raise TypeError(f"status_values must be dict, not {type(status_values)}")
        if not isinstance(next_url, str):
            raise TypeError(f"next_url must be str, not {type(next_url)}")
        if not isinstance(text, str):
            text = str(text)  # Force translated texts.
        signed_url = ""
        if next_url:
            signed_url = self._signer.sign(str(next_url))
        self._redis.hset(
            self._get_task_key(task_id, self.KEY_STATUS),
            mapping={
                "time": datetime.now(UTC).isoformat(),
                "status": TaskStatus.FINISHED.name,
                "result": result.name,
                "progress": "100.00",
                "status_values": json.dumps(status_values),
                "text": text,
                "next_url": signed_url,
            },
        )

    def get_task_status(self, task_id: str) -> Optional[DataStatus]:
        """
        Retrieve the status of a task.

        :param task_id: The ID of the task.
        :return: The status of the task, or None if the task does not exist or the data is corrupt.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        time_str, status_str, result_str, progress, status_values_json, text, next_url = self._redis.hmget(
            self._get_task_key(task_id, self.KEY_STATUS),
            ["time", "status", "result", "progress", "status_values", "text", "next_url"],
        )
        if not status_str:
            return None
        try:
            # We do not trust the data from the Redis store.
            time = datetime.fromisoformat(time_str)
            status = TaskStatus[status_str]
            result = TaskResult[result_str]
            progress = round(float(progress), 2)
            if not (0.0 <= progress <= 100.0):
                progress = 0.0
            if len(text) > 1000:
                text = ""
            if len(status_values_json) > 5000:
                status_values_json = ""
            if next_url:
                next_url = self._signer.unsign(next_url)
        except KeyError or ValueError or BadSignature:
            return None
        is_stop_requested, stop_request_time = self.get_task_stop_request(task_id)
        status_values = json.loads(status_values_json)
        if not isinstance(status_values, dict):
            status_values = {}
        for key, value in status_values.items():
            if not isinstance(value, str):
                status_values = {}
                break
        return DataStatus(
            time=time,
            status=status,
            result=result,
            progress=progress,
            status_values=status_values,
            text=text,
            next_url=next_url,
            stop_requested=is_stop_requested,
            stop_request_time=stop_request_time,
        )

    def set_task_stop_request(self, task_id: str, should_stop: bool) -> None:
        """
        Sets a stop request for a task in the data store.

        :param task_id: The ID of the task.
        :param should_stop: A flag indicating whether the task should be stopped.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        if not isinstance(should_stop, bool):
            raise TypeError(f"should_stop must be bool, not {type(should_stop)}")
        task_key = self._get_task_key(task_id, self.KEY_REQUEST_STOP)
        stop_request = f'{"true" if should_stop else "false"};{datetime.now(UTC).isoformat()}'
        self._redis.set(task_key, stop_request)

    def get_task_stop_request(self, task_id: str) -> Tuple[bool, datetime]:
        """
        Test if a task shall be stopped.

        :param task_id: The ID of the task.
        :return: `True` if a stop request has been made for the task, `False` otherwise.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        task_key = self._get_task_key(task_id, self.KEY_REQUEST_STOP)
        should_stop_str, time_str = self._redis.get(task_key).split(";")
        try:
            should_stop = should_stop_str == "true"
            time = datetime.fromisoformat(time_str)
        except ValueError:
            should_stop = False
            time = datetime.now(UTC)
        return should_stop, time

    def write_log(self, task_id: str, level: LogLevel, message: str, details: str):
        """
        Write a log entry.

        :param task_id: The ID of the task.
        :param level: The log level of the message.
        :param message: The log message.
        :param details: The log details.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        if not isinstance(level, LogLevel):
            raise TypeError(f"level must be DataLogLevel, not {type(level)}")
        if not isinstance(message, str):
            message = str(message)
        task_key = self._get_task_key(task_id, self.KEY_LOG)
        fields = {"level": str(level.value), "message": message, "details": details}
        self._redis.xadd(task_key, fields=fields, maxlen=5000)

    def read_log(self, task_id: str, after_timestamp: Optional[str] = None) -> list[dict[str, str]]:
        """
        Read a maximum of 100 of the last log entries for the task, optionally starting from a given timestamp.

        The result is a JSON compatible list of log entries, like:

        ```json
        [{'timestamp': '...', 'level': 'info', 'message': '...', 'details': '...'}, {...}, ...]
        ```

        :param task_id: The ID of the task.
        :param after_timestamp: Optional timestamp to retrieve only messages *after* this timestamp.
        :return: A JSON compatible list of log entries.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        if after_timestamp is not None and not isinstance(after_timestamp, str):
            raise TypeError(f"after_timestamp must be str, not {type(after_timestamp)}")
        task_key = self._get_task_key(task_id, self.KEY_LOG)
        streams = {task_key: after_timestamp or "0"}
        logs = self._redis.xread(streams, count=100, block=0)
        log_entries = []
        for timestamp, fields in logs[0]:
            level = fields["level"]
            message = fields["message"]
            details = fields["details"]
            log_entries.append(
                {"timestamp": str(timestamp), "level": str(level), "message": str(message), "details": str(details)}
            )
        log_entries.reverse()
        return log_entries

    def del_all_task_data(self, task_id: str) -> None:
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be str, not {type(task_id)}")
        self._redis.delete(
            self._get_task_key(task_id, self.KEY_STATUS),
            self._get_task_key(task_id, self.KEY_REQUEST_STOP),
            self._get_task_key(task_id, self.KEY_LOG),
        )


class LazyDataStore(LazyObject):
    def _setup(self):
        self._wrapped = DataStore()


data_store: Union[DataStore, LazyDataStore] = LazyDataStore()
