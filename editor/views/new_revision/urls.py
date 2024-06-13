#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


from django.urls import path

from editor.views.new_revision.assistant import NewRevisionAssistant
from editor.views.new_revision.checks import NewRevisionChecksView
from editor.views.new_revision.done import NewRevisionDoneView
from editor.views.new_revision.running import NewRevisionRunningView
from editor.views.new_revision.stop import NewRevisionStopView

urlpatterns = [
    path("", NewRevisionAssistant.as_view(), name="new_revision"),
    path("checks/", NewRevisionChecksView.as_view(), name="new_revision_checks"),
    path("running/", NewRevisionRunningView.as_view(), name="new_revision_running"),
    path("done/", NewRevisionDoneView.as_view(), name="new_revision_done"),
    path("stop/", NewRevisionStopView.as_view(), name="new_revision_stop"),
]
