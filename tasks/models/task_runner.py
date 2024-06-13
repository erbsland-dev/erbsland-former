#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models, transaction

from tasks.models.task_status import TaskStatus


class TaskRunner(models.Model):
    """
    A task runner is any object that is running tasks and is target of the run tasks.

    Therefore, a task runner must only run one task at a time. For this reason, you can
    test if there is already a task running.
    """

    def has_unfinished_tasks(self) -> bool:
        """
        Tests if there are not finished running tasks for this project.
        """
        return self.tasks.exclude(status=TaskStatus.FINISHED).exists()
