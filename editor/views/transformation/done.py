#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import humanize
from django.utils.translation import gettext_lazy as _

from backend.tools.statistic.statistic_field import StatisticField
from backend.tools.statistic.statistic_highlight import StatisticHighlight
from backend.transformer import TransformerBase
from design.views.assistant.generic import AssistantDoneView
from backend.tools.statistic.statistic import Statistic
from editor.views.transformation.access import TransformationAccessMixin


class TransformationDone(TransformationAccessMixin, AssistantDoneView):
    template_name = "editor/transformation/done.html"

    def get_success_url(self):
        return self.get_project_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statistic_values = self.assistant.transformation.statistics
        failures = statistic_values.get("failures", 0)
        changed_fragments = statistic_values.get("changed_fragments", 0)
        statistics_fields = [
            StatisticField("documents", _("Transformed Documents"), "file"),
            StatisticField("fragments", _("Transformed Fragments"), "cube"),
            StatisticField("changed_fragments", _("Changed Fragments"), "pen"),
            StatisticField(
                "failures",
                _("Failed Transformations"),
                "xmark",
                highlight=StatisticHighlight.BAD if failures > 0 else StatisticHighlight.NONE,
            ),
        ]
        transformer: TransformerBase = self.assistant.get_transformer()
        statistics_fields.extend(transformer.get_statistic_fields())
        context["statistic"] = Statistic.from_fields(statistics_fields, statistic_values)
        if changed_fragments:
            context["submit_text"] = _("Close Assistant and Review Changes")
        else:
            context["submit_text"] = _("Close Assistant")
        return context
