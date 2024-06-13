#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from backend.syntax_handler.base import SyntaxHandlerBase
from django.utils.translation import gettext_lazy as _


class PlainTextSyntaxHandler(SyntaxHandlerBase):
    """
    A syntax handler for plain text
    """

    name = "plainText"
    verbose_name = _("Plaintext")
    accepted_suffixes = ["txt"]
    markdown_block_identifier = "plain"
