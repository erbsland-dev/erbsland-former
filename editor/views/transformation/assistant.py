#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.shortcuts import redirect

from backend.enums.transformation_step import TransformationStep
from design.views.generic import PageView
from editor.views.transformation.access import TransformationAccessMixin


class TransformationAssistant(TransformationAccessMixin, PageView):
    """
    The initial view for the transformation assistant, redirecting to the current page.
    """

    def is_assistant_required(self):
        return False

    def get(self, request, *args, **kwargs):
        return redirect(self.get_step_url(self.get_current_step_value()))
