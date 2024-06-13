#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from design.views.generic import PageView
from editor.views.egress.access import EgressAccessMixin


class EgressRunningView(EgressAccessMixin, PageView):
    template_name = "design/assistant/task_running.html"
