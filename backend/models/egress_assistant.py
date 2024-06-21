#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.db import models, transaction
from django.db.models import QuerySet
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from backend.enums.egress_step import EgressStep
from backend.models import Document
from backend.models.project_assistant import ProjectAssistant
from backend.tools.definitions import PATH_LENGTH
from backend.tools.validators import egress_destination_validator
from tasks.models import Task
from tasks.models.task import TaskParameter


class EgressAssistant(ProjectAssistant):
    """
    An egress operation.

    This object holds all information that is required for the egress operation.
    """

    destination = models.CharField(max_length=32, validators=[egress_destination_validator])
    """The destination of the egress operation. Must be a value of `EgressDestination`."""

    working_directory = models.CharField(max_length=PATH_LENGTH, blank=True)
    """
    The relative path (to BACKEND_WORKING_DIR) of the working directory that was used to prepare and provide
    the egress data. It must be deleted when the assistant is closed to free any used resources.
    This directory is also used to find the resulting file for a download.
    """

    class Meta:
        verbose_name = _("Egress")

    def get_selected_documents(self) -> QuerySet[Document]:
        """
        Get all selected documents associated with this assistant.
        """
        selected_ids = [row["document__id"] for row in self.documents.order_by("order_index").values("document__id")]
        return Document.objects.filter(id__in=selected_ids).order_by(Lower("path"))

    def start_export(self, *, success_url: str, failure_url: str):
        """
        Start a new export.

        :param success_url: URL to redirect the user to after the export successfully completes.
        :param failure_url: URL to redirect if the export fails.
        """
        with transaction.atomic():
            if self.project.has_unfinished_tasks():
                raise ValueError(_("There is already a task running for this project."))
            input_data = {
                "egress_assistant_pk": str(self.pk),
            }
            task = Task.objects.start_task(
                TaskParameter(
                    task_runner=self.project.task_runner,
                    user=self.user,
                    action="egress",
                    input_data=input_data,
                    success_url=success_url,
                    failure_url=failure_url,
                    stopped_url=failure_url,
                )
            )
            self.step = EgressStep.RUNNING
            self.task = task
            self.save()
        # Clean up old tasks.
        Task.objects.clean_up()
