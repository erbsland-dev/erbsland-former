#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property

from django.utils.translation import gettext_lazy as _

from backend.enums.transformation_step import TransformationStep
from backend.models.transformation_assistant import TransformationAssistant
from editor.views.project import ProjectAccessMixin
from editor.views.project.assistant_mixin import ProjectAssistantMixin
from editor.views.transformation.steps import TransformationSteps


class TransformationAccessMixin(
    ProjectAssistantMixin[TransformationSteps, TransformationStep, TransformationAssistant], ProjectAccessMixin
):
    steps = TransformationSteps()
    page_icon_name = "magic-wand-sparkles"
    assistant_name = "transformation"
    assistant_model = TransformationAssistant
    assistant_step_enum = TransformationStep
    assistant_display_name = _("Transformation")
