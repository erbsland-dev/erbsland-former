#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from backend.models import Revision
from backend.models.project_assistant import ProjectAssistant
from backend.tools.definitions import NAME_LENGTH
from backend.tools.validators import name_validator
from tasks.models import Task
from tasks.models.task import TaskParameter


class RevisionAssistant(ProjectAssistant):
    """
    This model represents a running revision assistant.
    """

    revision_label = models.CharField(
        blank=True, max_length=NAME_LENGTH, validators=[name_validator], verbose_name=_("Revision Label")
    )
    """An optional label assigned to the new revision."""

    keep_fragments = models.BooleanField(
        default=False, verbose_name=_("Keep all split points from the selected version.")
    )
    """If the fragments shall be copied with no changes."""

    copy_review = models.BooleanField(default=False, verbose_name=_("Copy all review states into the new revision"))
    """If the fragments are kept, also copy the review states."""

    class Meta:
        verbose_name = _("New Revision Assistant")
        verbose_name_plural = _("New Revision Assistants")

    def start_new_revision(self, *, success_url: str, failure_url: str):
        """
        Start creating a new revision action.

        :param success_url: URL to redirect the user to after creating a new revision.
        :param failure_url: URL to redirect if creating a new revision fails.
        """
        with transaction.atomic():
            if self.project.has_unfinished_tasks():
                raise ValueError(_("There is already a task running for this project."))
            input_data = {
                "revision_assistant_pk": str(self.pk),
            }
            task = Task.objects.start_task(
                TaskParameter(
                    task_runner=self.project.task_runner,
                    user=self.user,
                    action="new_revision",
                    input_data=input_data,
                    success_url=success_url,
                    failure_url=failure_url,
                    stopped_url=failure_url,
                )
            )
            self.task = task
            self.save()
        # Clean up old tasks.
        Task.objects.clean_up()
