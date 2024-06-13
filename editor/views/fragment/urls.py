#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.urls import path

from editor.views.fragment.delete_edit import DeleteEditView
from editor.views.fragment.detail import FragmentDetailsView
from editor.views.fragment.edit import FragmentEditView
from editor.views.fragment.review import FragmentReviewView

urlpatterns = [
    path("", FragmentReviewView.as_view(), name="fragment"),
    path("details/", FragmentDetailsView.as_view(), name="fragment_details"),
    path("edit/", FragmentEditView.as_view(), name="fragment_edit"),
    path("delete_edit/", DeleteEditView.as_view(), name="fragment_delete_edit"),
]
