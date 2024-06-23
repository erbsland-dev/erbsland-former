#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

from editor.views.project import ProjectDetailView
from editor.views.project.home import UserHome
from editor.views.project.message import ProjectCannotEditView, ProjectNoPendingFragments
from editor.views.project.create import ProjectCreateView
from editor.views.project.delete import ProjectDeleteView
from editor.views.project.rename import ProjectRenameView

urlpatterns = [
    path("", UserHome.as_view(), name="user_home"),
    path("create/", ProjectCreateView.as_view(), name="project_create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="project"),
    path("<int:pk>/rename/", ProjectRenameView.as_view(), name="project_rename"),
    path("<int:pk>/delete/", ProjectDeleteView.as_view(), name="project_delete"),
    path("<int:pk>/rev-<int:revision>/", ProjectDetailView.as_view(), name="project"),
    path("<int:pk>/cannot_edit/", ProjectCannotEditView.as_view(), name="project_cannot_edit"),
    path("<int:pk>/no_pending/", ProjectNoPendingFragments.as_view(), name="project_no_pending"),
    path("<int:pk>/no_rejected/", ProjectNoPendingFragments.as_view(), name="project_no_rejected"),
]
