#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import logging
from typing import Optional

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from backend.syntax_handler import syntax_manager
from backend.tools.definitions import NAME_LENGTH, IDENTIFIER_LENGTH
from backend.tools.validators import identifier_validator
from tasks.models.task_runner import TaskRunner


class ProjectManager(models.Manager):
    """
    The manager for `Project` instances.
    """

    @transaction.atomic
    def create_project(self, name: str, description: str, owner: User, default_syntax: str = "") -> "Project":
        """
        Create a new project with a task runner and initial revision.

        :param name: The name of the project.
        :param description: An optional description.
        :param owner: The user that created and owns the project.
        :param default_syntax: Optional default syntax for the project.
        :return: The created object.
        """
        task_runner = TaskRunner.objects.create()
        if not default_syntax:
            default_syntax = syntax_manager.get_default_name()
        project = self.create(
            name=name,
            description=description,
            owner=owner,
            task_runner=task_runner,
            default_syntax=default_syntax,
        )
        project.revisions.create(number=1)
        return project


class Project(models.Model):
    """
    A project contains one or more processed files.
    """

    name = models.CharField(max_length=NAME_LENGTH)
    """The name of the project, set by the user."""

    description = models.TextField(blank=True)
    """The optional description of the project in Markdown format."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_models")
    """The owner of the document."""

    editors = models.ManyToManyField(User, related_name="edited_models")
    """Editors for the document"""

    default_syntax = models.CharField(max_length=IDENTIFIER_LENGTH, validators=[identifier_validator])
    """The default syntax"""

    task_runner = models.OneToOneField(TaskRunner, on_delete=models.CASCADE)
    """A reference to the task runner object."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the project was created."""

    modified = models.DateTimeField(auto_now=True)
    """The date when the project was last modified."""

    objects = ProjectManager()

    def __str__(self):
        return self.name

    def get_latest_revision(self):
        """
        Get the latest revision for this project.

        In case if the database is corrupt, try to fix a missing flag or revision.
        Usually, this is not a good idea, as it may lead to further problems when e.g. a running task caused the
        initial problem. In this case, if no latest version can be found, a project cannot even get accessed or
        deleted.
        """
        with transaction.atomic():
            try:
                revision = self.revisions.get(is_latest=True)
            except ObjectDoesNotExist:
                # In case the database is corrupt, try to recover it.
                if self.revisions.exists():
                    # If the `is_latest` flag is missing, add it to the latest revision.
                    logging.error("Database is corrupt. The `is_latest` flag is not set for any revision.")
                    logging.info("Attempting to repair the database.")
                    revision = self.revisions.order_by("-number").first()
                    revision.is_latest = True
                    revision.save()
                else:
                    # If there are no revisions, add an initial empty one.
                    logging.error("Database is corrupt. A project with no revisions exist. Attempting repair.")
                    logging.info("Attempting to repair the database.")
                    revision = self.revisions.create(number=1)
        return revision

    def get_latest_revision_number(self) -> int:
        """
        Get the latest revision number for this project.
        """
        return self.get_latest_revision().number

    def get_revisions(self, count: int):
        """
        Get a list of revisions, starting with the latest ones.

        :param count: The number of revisions in that list.
        :return: A query that returns the list.
        """
        return self.revisions.order_by("-number")[:count]

    def get_revision_count(self) -> int:
        """
        Get the number of revisions in this project.
        """
        return self.revisions.count()

    def get_document_count(self) -> int:
        """
        Get the number of documents.
        """
        return self.get_latest_revision().documents.count()

    def has_unfinished_tasks(self) -> bool:
        """
        Test if this project has unfinished tasks.
        """
        return self.task_runner.has_unfinished_tasks()

    def has_running_assistant(self) -> bool:
        from backend.models.project_assistant import ProjectAssistant

        try:
            return self.assistant is not None
        except ProjectAssistant.DoesNotExist:
            return False

    def get_running_assistant(self) -> Optional["ProjectAssistant"]:
        from backend.models.project_assistant import ProjectAssistant

        try:
            return self.assistant
        except ProjectAssistant.DoesNotExist:
            return False

    @property
    def can_be_edited(self) -> bool:
        """
        Test if the user can edit this project.
        """
        if self.has_running_assistant() or self.has_unfinished_tasks():
            return False
        return True

    @property
    def cannot_edit_reason(self) -> str:
        """
        Return a reason why the project can't be edited.
        """
        if self.has_running_assistant():
            return _("An assistant is currently running. Please finish this task or cancel it.")
        if self.has_unfinished_tasks():
            return _(
                "An operation is currently running in the background that modifies the project. "
                "Please wait until this operation is complete."
            )
        return _("An unknown reason prevents editing of this project.")

    def can_user_edit(self, user: User) -> bool:
        """
        Test if the given user can edit this project.

        :param user: The user to test.
        :return: `True` if the given user can edit this project.
        """
        if self.owner == user:
            return True
        return self.editors.filter(user=user).exists()

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        indexes = [
            models.Index(fields=["modified"], name="project_idx_modified"),
            models.Index(fields=["owner"], name="project_idx_owner"),
        ]
