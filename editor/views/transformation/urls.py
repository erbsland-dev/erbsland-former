#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


from django.urls import path

from editor.views.transformation.assistant import TransformationAssistant
from editor.views.transformation.done import TransformationDone
from editor.views.transformation.preview import TransformationPreview
from editor.views.transformation.profile import TransformationProfileView
from editor.views.transformation.running import TransformationRunning
from editor.views.transformation.setup import TransformationSetup
from editor.views.transformation.stop import TransformationStop

urlpatterns = [
    path("", TransformationAssistant.as_view(), name="transformation"),
    path("profile/", TransformationProfileView.as_view(), name="transformation_profile"),
    path("setup/", TransformationSetup.as_view(), name="transformation_setup"),
    path("preview/", TransformationPreview.as_view(), name="transformation_preview"),
    path("preview/<int:document_id>/", TransformationPreview.as_view(), name="transformation_preview_document"),
    path("running/", TransformationRunning.as_view(), name="transformation_running"),
    path("done/", TransformationDone.as_view(), name="transformation_done"),
    path("stop/", TransformationStop.as_view(), name="transformation_stop"),
]
