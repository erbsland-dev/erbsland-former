#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _


class IngestPlanedAction(IntegerChoices):
    """
    The planed action for a single document.
    """

    IGNORE = 0, _("Ignore")
    """The document is ignored."""

    ADD = 1, _("Add")
    """The document is added to the project."""
