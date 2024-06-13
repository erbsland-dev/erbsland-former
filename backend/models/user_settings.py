#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserSettings(models.Model):
    """
    The profile where a user can store its preferences and settings.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")

    class Meta:
        verbose_name = _("User Settings")
