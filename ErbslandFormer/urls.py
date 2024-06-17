#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include

urlpatterns = i18n_patterns(
    path("", include("editor.urls")),
    path("", include("design.urls")),
    path("task/", include("tasks.urls")),
    path("accounts/", include("bulma_auth.urls")),
    prefix_default_language=False,
)
