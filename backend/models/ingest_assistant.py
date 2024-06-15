#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from backend.enums import IngestStep
from backend.models.project_assistant import ProjectAssistant
from backend.storage import working_storage
from backend.tools.definitions import IDENTIFIER_LENGTH, PATH_LENGTH
from backend.tools.validators import identifier_validator
from tasks.models.task import Task, TaskParameter


def get_storage():
    return working_storage


class IngestAssistant(ProjectAssistant):
    """
    An ingest operation.

    This object holds all information that is required for the ingest operation.
    """

    uploaded_file = models.FileField(upload_to="uploads/", storage=get_storage())
    """The uploaded file that is the source for this ingest operation."""

    minimum_fragment_size = models.PositiveBigIntegerField(verbose_name=_("Minimum Fragment Size"), default=0)
    """The minimum size of a text fragment."""

    maximum_fragment_size = models.PositiveBigIntegerField(verbose_name=_("Maximum Fragment Size"), default=1024)
    """The maximum size of a text fragment."""

    size_unit = models.CharField(max_length=IDENTIFIER_LENGTH, validators=[identifier_validator])
    """The unit that is used for the size calculation."""

    working_directory = models.CharField(max_length=PATH_LENGTH, blank=True)
    """
    The relative path (to BACKEND_WORKING_DIR) of the working directory that was used to prepare and provide
    the ingress data. It must be deleted when the assistant is closed to free any used resources.
    """

    class Meta:
        verbose_name = _("Ingest")

    def _start_task(
        self,
        required_step: IngestStep,
        next_step: IngestStep,
        action_name: str,
        success_url: str,
        failure_url: str,
    ):
        """
        Start the next task.

        :param required_step: The minimum required step to start this action.
        :param next_step: The next step to transition to.
        :param action_name: The name of the action to be started in the background.
        :param success_url: The URL that is shown when the task successfully finishes.
        :param failure_url: The URL that is shown on any problem.
        """
        with transaction.atomic():
            if self.project.has_unfinished_tasks():
                raise ValueError(_("There is already a task running for this project."))
            steps = list(IngestStep)
            if steps.index(self.step) < steps.index(required_step) or self.step == IngestStep.DONE:
                raise ValueError(_("The ingest operation is in the wrong state."))
            self.step = next_step
            self.save()
            input_data = {"ingest_pk": str(self.pk)}
            task = Task.objects.start_task(
                TaskParameter(
                    task_runner=self.project.task_runner,
                    user=self.user,
                    action=action_name,
                    input_data=input_data,
                    success_url=success_url,
                    failure_url=failure_url,
                    stopped_url=failure_url,
                )
            )
            self.task = task
            self.save()
        # Also clean up old tasks
        Task.objects.clean_up()

    def analyze_upload(self, success_url: str, failure_url: str) -> None:
        """
        Start analyzing the upload.
        """
        self._start_task(
            IngestStep.UPLOAD,
            IngestStep.ANALYSIS_RUNNING,
            "ingest_analyze_upload",
            success_url,
            failure_url,
        )

    def generate_preview(self, success_url: str, failure_url: str) -> None:
        """
        After the setup, generate the split preview for documents.
        """
        self._start_task(
            IngestStep.SETUP,
            IngestStep.PREPARING_PREVIEW,
            "ingest_generate_preview",
            success_url,
            failure_url,
        )

    def import_previewed_documents(self, success_url: str, failure_url: str) -> None:
        """
        After the preview, import the documents into the project.
        """
        self._start_task(
            IngestStep.PREVIEW,
            IngestStep.IMPORTING_DOCUMENTS,
            "ingest_import_documents",
            success_url,
            failure_url,
        )
