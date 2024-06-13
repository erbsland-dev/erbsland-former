#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from backend.enums.ingest_step import IngestStep
from backend.models import IngestAssistant
from editor.views.ingest.steps import IngestSteps
from editor.views.project import ProjectAccessMixin
from editor.views.project.assistant_mixin import ProjectAssistantMixin


class IngestAccessMixin(ProjectAssistantMixin[IngestSteps, IngestStep, IngestAssistant], ProjectAccessMixin):
    steps = IngestSteps()
    stop_page_name = "ingest_stop"
    assistant_name = "ingest"
    assistant_model = IngestAssistant
    assistant_step_enum = IngestStep
    assistant_display_name = _("Import")
