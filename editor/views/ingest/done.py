#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.utils.translation import gettext_lazy as _

from backend.size_calculator.manager import size_calculator_manager
from backend.tools.statistic.statistic_field import StatisticField
from design.views.assistant.generic import AssistantDoneView
from backend.tools.statistic.statistic import Statistic
from .access import IngestAccessMixin


class IngestDone(IngestAccessMixin, AssistantDoneView):
    intro_text = _("All documents from the preview were imported into the latest revision of your project.")

    def get_success_url(self):
        return self.get_project_url()

    def get_form_submit_text(self) -> str:
        return _("Close Assistant and Continue to Project")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statistics_fields = [
            StatisticField("documents", _("Imported Documents"), "file"),
            StatisticField("fragments", _("Imported Fragments"), "cube"),
            StatisticField("units", size_calculator_manager.verbose_name(self.assistant.size_unit), "file"),
            StatisticField("bytes", _("Imported Bytes"), "download"),
            StatisticField("characters", _("Imported Characters"), "e"),
            StatisticField("words", _("Imported Words"), "w"),
            StatisticField("lines", _("Imported Lines"), "align-left"),
        ]
        ingest_statistics = self.assistant.statistics
        context["statistic"] = Statistic.from_fields(statistics_fields, ingest_statistics)
        return context
