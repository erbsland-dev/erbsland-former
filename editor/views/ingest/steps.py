#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from backend.enums.ingest_step import IngestStep
from design.views.assistant.steps_base import AssistantStepsBase
from design.views.assistant.step_definition import AssistantStepDefinition


class IngestStepDefinition(AssistantStepDefinition[IngestStep]):
    pass


class IngestSteps(AssistantStepsBase[IngestStepDefinition]):
    step_definitions = [
        IngestStepDefinition(IngestStep.UPLOAD, "ingest_upload", _("Upload File")),
        IngestStepDefinition(IngestStep.ANALYSIS_RUNNING, "ingest_analyze", _("Analyze Files"), is_transition=True),
        IngestStepDefinition(IngestStep.SETUP, "ingest_setup", _("Setup")),
        IngestStepDefinition(
            IngestStep.PREPARING_PREVIEW, "ingest_preparing_preview", _("Preparing Preview"), is_transition=True
        ),
        IngestStepDefinition(IngestStep.PREVIEW, "ingest_preview", _("Preview")),
        IngestStepDefinition(
            IngestStep.IMPORTING_DOCUMENTS, "ingest_import", _("Importing Documents"), is_transition=True
        ),
        IngestStepDefinition(IngestStep.DONE, "ingest_done", _("Done")),
    ]
