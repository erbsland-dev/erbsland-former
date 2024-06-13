#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

import editor.views.ingest as ingest

urlpatterns = [
    path("", ingest.IngestAssistant.as_view(), name="ingest"),
    path("upload/", ingest.IngestUpload.as_view(), name="ingest_upload"),
    path("analyze/", ingest.IngestTaskRunning.as_view(), name="ingest_analyze"),
    path("setup/", ingest.IngestSetup.as_view(), name="ingest_setup"),
    path(
        "preparing_preview/",
        ingest.IngestTaskRunning.as_view(),
        name="ingest_preparing_preview",
    ),
    path("preview/", ingest.IngestPreview.as_view(), name="ingest_preview"),
    path(
        "preview/<int:document_id>/",
        ingest.IngestPreview.as_view(),
        name="ingest_preview_with_id",
    ),
    path("import/", ingest.IngestTaskRunning.as_view(), name="ingest_import"),
    path("done/", ingest.IngestDone.as_view(), name="ingest_done"),
    path("stop/", ingest.IngestStop.as_view(), name="ingest_stop"),
]
