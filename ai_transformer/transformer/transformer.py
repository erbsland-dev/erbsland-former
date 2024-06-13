#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.utils.translation import gettext_lazy as _

from ai_transformer.tools.constants import (
    STATUS_TOTAL_TOKENS,
    STATUS_TOTAL_COST,
    STATISTIC_COMPLETION_TOKENS,
    STATISTIC_PROMPT_TOKENS,
    STATISTIC_TOTAL_TOKENS,
    STATISTIC_TOTAL_COST,
)
from backend.tools.statistic.statistic_field import StatisticField
from backend.transformer import TransformerBase
from ai_transformer.transformer.processor import AiProcessor
from ai_transformer.transformer.profile_settings_handler import AiProfileSettingsHandler
from ai_transformer.transformer.user_settings_handler import AiUserSettingsHandler
from tasks.actions.status import TaskStatusField


class AiTransformer(TransformerBase):
    """
    A transformer that uses one or more regular expression replacements to edit texts.
    """

    name = "gpt_edit"
    verbose_name = "GPT Text Processor"
    description = _(
        """\
        Use this transformer using prompts for an OpenAI GPT model, verify and use the output from
        the model to edit texts.
        """
    )
    version = 1
    user_settings_class = AiUserSettingsHandler
    profile_settings_class = AiProfileSettingsHandler
    processor_class = AiProcessor
    title_background_color_class = "has-background-ai-transformer-40"
    short_name = "GPT"
    icon_name = "hat-wizard"
    status_fields = [
        TaskStatusField(STATUS_TOTAL_TOKENS, _("Used Tokens"), "—", "file"),
        TaskStatusField(STATUS_TOTAL_COST, _("Estimated Cost"), "—", "money-bill"),
    ]
    statistic_fields = [
        StatisticField(STATISTIC_COMPLETION_TOKENS, _("Completion Token Usage"), "file"),
        StatisticField(STATISTIC_PROMPT_TOKENS, _("Used Prompt Token Usage"), "file"),
        StatisticField(STATISTIC_TOTAL_TOKENS, _("Total Token Usage"), "file"),
        StatisticField(STATISTIC_TOTAL_COST, _("Estimated Cost for this Transformation"), "money-bill"),
    ]
