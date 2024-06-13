#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _


class TransformedStates(IntegerChoices):
    EMPTY = 0, _("Transform only fragments with no transformations")
    ERRORS = 1, _("Transform fragments with errors or no transformations")
    NO_EDITS = 2, _("Transform all fragments, except ones with manual edits")
    ALL = 3, _("Transform all fragments")
