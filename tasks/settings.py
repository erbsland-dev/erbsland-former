#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
"""
The settings module for the "tasks" application.

* Use keys prefixed with `TASKS_CELERY_*` to configure the celery system.
* "Redis" is used as broker for *Celery* but also as broker for real time task updates and logs.
  Make sure Celery (`TASKS_CELERY_...) and the app (`TASKS_DATA_REDIS_...`) do not share the same
  instance or database on Redis.
"""

TASKS_CELERY_BROKER_URL: str = "redis://127.0.0.1/"
"""The broker URL for the celery application."""

TASKS_CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
"""Retry to connect to the broker at startup.."""

TASKS_CELERY_TASK_SOFT_TIME_LIMIT: int = 24 * 60 * 60
"""Allow a task to run for 24 hours. Soft timeout."""

TASKS_CELERY_TASK_TIME_LIMIT: int = 24 * 60 * 60 + 60
"""Allow a task to run for 24 hours. Hard timeout +60 seconds after soft timeout."""

TASKS_DATA_REDIS_HOST: str = "127.0.0.1"
"""The redis configuration for the tasks system. The hostname or IP address."""

TASKS_DATA_REDIS_PORT: int = 6379
"""The redis configuration for the tasks system. The port."""

TASKS_DATA_REDIS_DB_NUM: int = 1
"""The redis configuration for the tasks system. The DB number. """
