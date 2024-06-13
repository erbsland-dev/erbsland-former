#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from backend.enums import ReviewState, ReviewStateCounts
from backend.enums.transformation_state import TransformationStateCounts
from backend.tools.definitions import NAME_LENGTH
from backend.tools.validators import name_validator


class Revision(models.Model):
    """
    A revision of a project.
    """

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="revisions")
    """The project that is owning the version."""

    number = models.IntegerField()
    """The sequence number of the reversion, starting from 1."""

    label = models.CharField(max_length=NAME_LENGTH, blank=True, validators=[name_validator])
    """An optional label to mark a version."""

    is_latest = models.BooleanField(default=True)
    """A flag is this revision is the latest."""

    predecessor = models.ForeignKey("Revision", null=True, related_name="successors", on_delete=models.SET_NULL)
    """The predecessor of this revision."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the revision was created."""

    modified = models.DateTimeField(auto_now=True)
    """The date when the revision was last modified."""

    def __str__(self) -> str:
        if self.label:
            return f"{self.number} - {self.label}"
        return f"{self.number}"

    @property
    def can_be_deleted(self) -> bool:
        """
        If this revision can be deleted.
        """
        if self.number <= 1:
            return False  # Do not allow to delete the first revision of a project.
        return not self.successors.exists()

    def review_states(self) -> ReviewStateCounts:
        """
        Get the number of review states for this revision.
        """
        from backend.models.fragment import Fragment

        node_ids = set([row["id"] for row in self.documents.values("id")])
        states = (
            Fragment.objects.filter(document_id__in=node_ids).values("review_state").annotate(total=models.Count("id"))
        )
        result: dict[ReviewState, int] = {}
        for state in states:
            result[ReviewState(state["review_state"])] = state["total"]
        return ReviewStateCounts.from_dict(result)

    def transformation_states(self) -> TransformationStateCounts:
        from backend.models.document import Document

        return Document.transformation_states_from_documents(self.documents)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.is_latest:
            # Set all other revisions for the same project to is_latest=False
            Revision.objects.filter(project=self.project, is_latest=True).update(is_latest=False)
        super().save()

    class Meta:
        verbose_name = _("Revision")
        verbose_name_plural = _("Revisions")
        indexes = [
            models.Index(fields=["project", "number"], name="revision_number_idx"),
            models.Index(fields=["project", "is_latest"], name="revision_is_latest_idx"),
        ]
