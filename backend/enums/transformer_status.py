#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _


class TransformerStatus(models.IntegerChoices):
    """
    The status of an automated transformer process.
    """

    FAILURE = 0, _("Failure")
    SUCCESS = 1, _("Success")
