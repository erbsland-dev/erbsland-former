#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models.enums import IntegerChoices


class TaskResult(IntegerChoices):
    NONE = (0, "None")
    """There is no result yet."""

    SUCCESS = (1, "Success")
    """The task performed the action successfully."""

    FAILURE = (2, "Failure")
    """The task encountered an unexpected failure (e.g. exception)."""

    STOPPED = (3, "Stopped")
    """The user stopped the task."""
