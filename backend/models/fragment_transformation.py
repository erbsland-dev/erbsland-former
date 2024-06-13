#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models

from backend.enums import TransformerStatus
from .content_user import ContentUser
from .fragment import Fragment


class FragmentTransformation(ContentUser):
    """
    An automated transformation for a fragment.
    """

    fragment = models.OneToOneField(
        Fragment,
        on_delete=models.CASCADE,
        related_name="transformation",
    )
    """The fragment for this transformation."""

    status = models.SmallIntegerField(choices=TransformerStatus.choices, default=TransformerStatus.FAILURE.value)
    """The status of the transformer"""

    output = models.TextField(blank=True)
    """Raw output of the transformer."""

    failure_input = models.TextField(blank=True)
    """The input that caused to the failure if applicable (e.g. language model prompt)."""

    failure_reason = models.TextField(blank=True)
    """The reason for a failure, like a detailed error message."""

    transformation = models.ForeignKey("Transformation", null=True, on_delete=models.SET_NULL)
    """The transformation that created this result."""

    @property
    def is_success(self):
        return self.status == TransformerStatus.SUCCESS.value

    @property
    def is_failure(self):
        return self.status == TransformerStatus.FAILURE.value

    class Meta:
        verbose_name = "Document Fragment Transformation"
        verbose_name_plural = "Document Fragment Transformation"
