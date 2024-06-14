#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from backend.transformer import TransformerBase
from django.utils.translation import gettext_lazy as _

from regex_transformer.transformer.processor import RegExProcessor
from regex_transformer.transformer.profile_settings_handler import RegExProfileSettingsHandler


class RegExTransformer(TransformerBase):
    """
    A transformer that uses one or more regular expression replacements to edit texts.
    """

    name = "regex_edit"
    verbose_name = "Regular Expression Based Text Editor"
    description = _("Use this transformer to edit text using one or more regular expressions.")
    version = 1
    profile_settings_class = RegExProfileSettingsHandler
    processor_class = RegExProcessor
    title_background_color_class = "has-background-re-transformer-dark"
    short_name = "RE"
    icon_name = "code"
