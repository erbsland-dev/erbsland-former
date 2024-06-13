#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from editor.views.egress.assistant import EgressAssistantView
from editor.views.egress.done import EgressDoneView
from editor.views.egress.download import EgressDownloadView
from editor.views.egress.running import EgressRunningView
from editor.views.egress.setup import EgressSetupView
from editor.views.egress.stop import EgressStopView

urlpatterns = [
    path("", EgressAssistantView.as_view(), name="egress"),
    path("setup/", EgressSetupView.as_view(), name="egress_setup"),
    path("running/", EgressRunningView.as_view(), name="egress_running"),
    path("done/", EgressDoneView.as_view(), name="egress_done"),
    path("stop/", EgressStopView.as_view(), name="egress_stop"),
    path("download/", EgressDownloadView.as_view(), name="egress_download"),
]
