#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.tools.definitions import IDENTIFIER_LENGTH, NAME_LENGTH
from backend.tools.validators import identifier_validator, name_validator


class Transformation(models.Model):
    """
    A transformation that was applied to a project or parts of it.
    This is a copy of the transformer settings that were used at the time the transformation was
    applied to keep them as reference for investigation or recreating a new transformation.
    While there is a link to the original profile, deleting the original profile does not affect this copy.
    """

    revision = models.ForeignKey("Revision", on_delete=models.CASCADE, related_name="transformations")
    """Assign the transformation to the revision, and therefore indirectly to the project."""

    transformer_name = models.CharField(max_length=IDENTIFIER_LENGTH, validators=[identifier_validator])
    """The name of the transformer that was used."""

    profile = models.ForeignKey("TransformerProfile", null=True, on_delete=models.SET_NULL, related_name="+")
    """The original profile from which this transformation was executed."""

    profile_name = models.CharField(max_length=NAME_LENGTH, validators=[name_validator])
    """A copy of the name of the profile, set by the user."""

    version = models.IntegerField()
    """The version of the transformer for which this settings were created."""

    configuration = models.JSONField()
    """The configuration for the transformer profile."""

    statistics = models.JSONField(default=dict)
    """Statistics about the transformation. Stored as JSON dictionary to make it extensible over time."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the project was created."""

    class Meta:
        verbose_name = _("Transformation")
        verbose_name_plural = _("Transformations")
        indexes = [
            models.Index(fields=["revision", "created"], name="tra_project_created_idx"),
        ]
