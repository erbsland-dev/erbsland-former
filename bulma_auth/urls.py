#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path

import bulma_auth.views as views

urlpatterns = [
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("password_change/", views.PasswordChange.as_view(), name="password_change"),
    path(
        "password_change/done/",
        views.PasswordChangeDone.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", views.PasswordReset.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        views.PasswordResetDone.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetComplete.as_view(),
        name="password_reset_complete",
    ),
]
