#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.shortcuts import redirect

from design.views.generic import PageView
from .access import EgressAccessMixin


class EgressAssistantView(EgressAccessMixin, PageView):
    """
    An easy selector that redirects to the current step of the assistant or to display
    the progress for a running task.
    """

    def is_assistant_required(self):
        return False

    def get(self, request, *args, **kwargs):
        return redirect(self.get_step_url(self.get_current_step_value()))
