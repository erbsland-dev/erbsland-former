#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class LineEndings(TextChoices):
    """
    The planed action for a single document.
    """

    LF = "lf", _("LF")
    CRLF = "crlf", _("CR/LF")
