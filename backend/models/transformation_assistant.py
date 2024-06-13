#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.db import models, transaction
from django.db.models import QuerySet, Count, F
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from backend.models.project_assistant import ProjectAssistant
from backend.enums.review_state import ReviewState
from backend.enums.transformer_status import TransformerStatus
from backend.enums.transformation_step import TransformationStep
from backend.enums.transformed_states import TransformedStates
from backend.models.fragment import Fragment
from backend.models.document import Document
from tasks.models import Task
from tasks.models.task import TaskParameter


class TransformationAssistant(ProjectAssistant):
    """
    This model represents a running transformation assistant. It is used while the user setups a transformation
    and while the transformation is running. After the background process finishes, a `Transformation` instance
    is added to the project and the assistant instance is removed.
    """

    profile = models.ForeignKey("TransformerProfile", on_delete=models.RESTRICT, related_name="+")
    """The transformer profile associated with this assistant."""

    transformed_states = models.IntegerField(choices=TransformedStates, default=TransformedStates.EMPTY)
    """How to handle fragments that are already processed."""

    review_unprocessed = models.BooleanField(default=True)
    """If unchanged fragments shall be processed."""

    review_pending = models.BooleanField(default=False)
    """If pending fragments shall be processed."""

    review_approved = models.BooleanField(default=False)
    """If approved fragments shall be processed."""

    review_rejected = models.BooleanField(default=True)
    """If rejected fragments shall be processed."""

    auto_approve_unchanged = models.BooleanField(default=True)
    """If unchanged fragments shall be automatically accepted."""

    stop_consecutive_failures = models.PositiveSmallIntegerField(default=10)
    """The transformation process stops if the given number of consecutive failures happen. 0=disabled"""

    stop_total_failures = models.PositiveSmallIntegerField(default=0)
    """The transformation process stops after encountering this total number of failures. 0=disabled."""

    rollback_on_failure = models.BooleanField(default=True)
    """If enabled, if the transformation process as a whole is failing, all changes are rolled back."""

    transformation = models.OneToOneField("Transformation", null=True, on_delete=models.SET_NULL, related_name="+")
    """The transformation that was created by this assistant."""

    failure_reason = models.TextField(blank=True)
    """If the transformation failed gracefully, this field is set to display the failure reason."""

    class Meta:
        verbose_name = _("Transformation Assistant")
        verbose_name_plural = _("Transformation Assistants")

    def get_review_states(self) -> list[ReviewState]:
        """
        Get a list of review states that were selected in this assistant.
        :return:
        """
        result = []
        if self.review_unprocessed:
            result.append(ReviewState.UNPROCESSED)
        if self.review_pending:
            result.append(ReviewState.PENDING)
        if self.review_approved:
            result.append(ReviewState.APPROVED)
        if self.review_rejected:
            result.append(ReviewState.REJECTED)
        return result

    def get_selected_documents(self) -> QuerySet[Document]:
        """
        Get all selected documents associated with this assistant.
        """
        selected_ids = [row["document__id"] for row in self.documents.order_by("order_index").values("document__id")]
        return Document.objects.filter(id__in=selected_ids).order_by(Lower("path"))

    def get_selected_fragments(self) -> QuerySet[Fragment]:
        """
        Get all selected fragments for this assistant, that match the criteria.
        :return:
        """
        document_ids = [row["id"] for row in self.get_selected_documents().values("id").order_by("id")]
        fragments = Fragment.objects.filter(document_id__in=document_ids).select_related("transformation", "edit")
        review_states = self.get_review_states()
        if len(review_states) < 3:
            fragments = fragments.filter(review_state__in=review_states)
        match self.transformed_states:
            case TransformedStates.EMPTY:
                fragments = fragments.exclude(transformation__isnull=False)
            case TransformedStates.ERRORS:
                fragments = fragments.exclude(transformation__status=TransformerStatus.SUCCESS)
            case TransformedStates.NO_EDITS:
                fragments = fragments.exclude(edit__isnull=False)
            case TransformedStates.ALL:
                pass
        return fragments

    def get_documents_from_fragments(self, fragments: QuerySet[Fragment]) -> list[dict]:
        """
        Given a queryset of fragments, get all the documents.

        :param fragments: A queryset of fragments.
        :return: A query set of document counts and document objects.
        """
        fragment_counts = (
            fragments.values("document")
            .annotate(fragment_count=Count("document"), path=F("document__path"))
            .order_by("path")
        )
        document_ids = [fragment_count["document"] for fragment_count in fragment_counts]
        documents_with_counts = []
        if document_ids:
            documents = Document.objects.filter(id__in=document_ids)
            documents_dict = {document.id: document for document in documents}
            for fragment_count in fragment_counts:
                document_id = fragment_count["document"]
                count = fragment_count["fragment_count"]
                document = documents_dict.get(document_id)
                if document:
                    documents_with_counts.append({"count": count, "document": document})
        return documents_with_counts

    def get_transformer(self) -> "TransformerBase":
        """
        Get the transformer instance associated with this assistant.
        """
        from backend.transformer.manager import transformer_manager

        return transformer_manager.get_transformer(self.profile.transformer_name)

    def transform_selected_fragments(self, success_url: str, failure_url: str):
        """
        Start to transform the selected document fragments.

        :param success_url: The URL that is displayed on success.
        :param failure_url: The URL that is displayed of the operation fails.
        """

        with transaction.atomic():
            if self.project.has_unfinished_tasks():
                raise ValueError(_("There is already a task running for this project."))
            if self.step in [
                TransformationStep.PROFILE.value,
                TransformationStep.SETUP.value,
                TransformationStep.DONE.value,
            ]:
                raise ValueError(_("The transformation operation is in the wrong state."))
            self.step = TransformationStep.TRANSFORMATION_RUNNING
            self.save()
            input_data = {
                "transformation_assistant_pk": str(self.pk),
            }
            transformer = self.get_transformer()
            status_fields = transformer.get_status_fields()
            task = Task.objects.start_task(
                TaskParameter(
                    task_runner=self.project.task_runner,
                    user=self.user,
                    action="transform_fragments",
                    input_data=input_data,
                    success_url=success_url,
                    failure_url=failure_url,
                    stopped_url=failure_url,
                    additional_status_fields=status_fields,
                )
            )
            self.task = task
            self.save()
        # Clean up old tasks.
        Task.objects.clean_up()
