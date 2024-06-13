#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from celery import Celery

import tasks

app = Celery("tasks")
app.config_from_object(tasks.settings, namespace="TASKS_CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
