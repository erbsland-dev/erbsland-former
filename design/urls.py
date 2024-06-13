#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path(
        "jsi18n/",
        cache_page(60 * 60)(JavaScriptCatalog.as_view()),
        name="javascript-catalog",
    ),
]
