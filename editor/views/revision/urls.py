#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from editor.views.revision.all import AllRevisionsView
from editor.views.revision.delete import RevisionDeleteView
from editor.views.revision.label import RevisionEditLabelView

urlpatterns = [
    path("", AllRevisionsView.as_view(), name="revision_all"),
    path("<int:revision>/delete/", RevisionDeleteView.as_view(), name="revision_delete"),
    path("<int:revision>/edit_label/", RevisionEditLabelView.as_view(), name="revision_edit_label"),
]
