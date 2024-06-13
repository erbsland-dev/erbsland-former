#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import uuid

from django.contrib.auth.models import User
from django.db import models

from tasks.models import Task


class ProjectAssistant(models.Model):
    """
    This model represents a running assistant for a project.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """A unique ID for the assistant."""

    project = models.OneToOneField("Project", on_delete=models.CASCADE, related_name="assistant")
    """The current assistant for this project. Only one per project can be active."""

    revision = models.ForeignKey("Revision", on_delete=models.CASCADE, related_name="+")
    """The revision this assistant was started for, if this is relevant."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    """The user that started this assistant."""

    assistant_name = models.CharField(max_length=32)
    """The name (identifier) of the assistant."""

    step = models.CharField(max_length=32, blank=False, name=False)
    """The current step in the assistant."""

    task = models.OneToOneField(Task, null=True, on_delete=models.SET_NULL, related_name="+")
    """A running task for this assistant."""

    statistics = models.JSONField(default=dict)
    """Statistics collected while running the assistant."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the assistant was created."""

    def get_verbose_assistant_name(self):
        """Get a verbose name for this assistant."""
        return self.assistant_name.replace("_", " ").title()

    class Meta:
        indexes = [
            models.Index(fields=["project", "user"], name="assist_main_idx"),
            models.Index(fields=["project"], name="ingest_idx_project"),
        ]
