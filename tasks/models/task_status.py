#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models.enums import IntegerChoices


class TaskStatus(IntegerChoices):
    """
    The status of a task.
    """

    CREATED = (0, "Created")
    """The task was created, but it was not started in the task queue yet."""

    RUNNING = (1, "Running")
    """The task is running in the task queue."""

    FINISHED = (2, "Finished")
    """The task finished, successfully or with errors."""
