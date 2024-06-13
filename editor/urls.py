#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path, include

import editor.views as views
from editor.views.document.detail import DocumentView
from editor.views.settings.user import UserSettingsView

urlpatterns = [
    path("", views.home.Home.as_view(), name="home"),
    path("welcome/", views.Welcome.as_view(), name="welcome"),
    path("project/", include("editor.views.project.urls")),
    path("project/<int:pk>/new_revision/", include("editor.views.new_revision.urls")),
    path("project/<int:pk>/ingest/", include("editor.views.ingest.urls")),
    path("project/<int:pk>/egress/", include("editor.views.egress.urls")),
    path("project/<int:pk>/revision/", include("editor.views.revision.urls")),
    path("project/<int:pk>/transformation/", include("editor.views.transformation.urls")),
    path("document/<int:pk>/", DocumentView.as_view(), name="document"),
    path("fragment/<int:pk>/", include("editor.views.fragment.urls")),
    path("transformer/", include("editor.views.transformer.urls")),
    path("user_settings/", UserSettingsView.as_view(), name="user_settings"),
    path("user_settings/<str:setting_page>/", UserSettingsView.as_view(), name="user_settings"),
]
