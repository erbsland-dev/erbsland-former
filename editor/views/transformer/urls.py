#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from editor.views.transformer.create import TransformerCreateView
from editor.views.transformer.delete import TransformerDeleteView
from editor.views.transformer.detail import TransformerDetailView
from editor.views.transformer.list import TransformerListView
from editor.views.transformer.rename import TransformerRenameView

urlpatterns = [
    path("", TransformerListView.as_view(), name="transformer"),
    path("create/", TransformerCreateView.as_view(), name="transformer_create"),
    path("<int:pk>/", TransformerDetailView.as_view(), name="transformer_edit"),
    path("<int:pk>/delete/", TransformerDeleteView.as_view(), name="transformer_delete"),
    path("<int:pk>/rename/", TransformerRenameView.as_view(), name="transformer_rename"),
]
