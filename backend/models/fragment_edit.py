#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models

from backend.tools.validators import markdown_validator
from .content_user import ContentUser
from .fragment import Fragment
from .learning_set import LearningSet


class FragmentEdit(ContentUser):
    """
    The human edit of a document fragment.
    """

    fragment = models.OneToOneField(Fragment, on_delete=models.CASCADE, related_name="edit")
    """The fragment of this edit."""

    notes = models.TextField(blank=True, default="", validators=[markdown_validator])
    """User notes about the manual edit."""

    learning_sets = models.ManyToManyField(LearningSet, related_name="edits")
    """The learning sets that use the edits from this fragment."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the fragment was created."""

    modified = models.DateTimeField(auto_now=True)
    """The date when the fragment was last modified."""

    class Meta:
        verbose_name = "Document Fragment Edit"
        verbose_name_plural = "Document Fragment Edits"
