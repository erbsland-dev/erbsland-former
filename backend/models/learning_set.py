#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.db import models

from backend.tools.definitions import NAME_LENGTH
from backend.tools.validators import name_validator


class LearningSet(models.Model):
    """
    A learning set to train a language model using manual edits.
    """

    name = models.CharField(max_length=NAME_LENGTH, validators=[name_validator])
    """The display name of the learning set."""

    notes = models.TextField(blank=True)
    """User notes for this learning set."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_learning_sets")
    """The owner of the learning set."""

    users = models.ManyToManyField(User, related_name="used_learning_sets")
    """Users than can use this learning set."""
