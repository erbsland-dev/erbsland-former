#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.urls import path

from editor.views.admin.admin_add import AdminAddView
from editor.views.admin.home import AdminHomeView
from editor.views.admin.user_add import UserAddView
from editor.views.admin.user_delete import UserDeleteView
from editor.views.admin.user_edit import UserEditView
from editor.views.admin.user_reset_pw import UserResetPwView

urlpatterns = [
    path("", AdminHomeView.as_view(), name="admin_home"),
    path("user/add/", UserAddView.as_view(), name="admin_user_add"),
    path("user/add_admin/", AdminAddView.as_view(), name="admin_user_add_admin"),
    path("user/<int:pk>/", UserEditView.as_view(), name="admin_user_edit"),
    path("user/<int:pk>/delete/", UserDeleteView.as_view(), name="admin_user_delete"),
    path("user/<int:pk>/reset_pw/", UserResetPwView.as_view(), name="admin_user_reset_pw"),
]
