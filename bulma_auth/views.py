#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import django.contrib.auth.views as auth_views
from django.forms import Form
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from bulma_forms.tools import add_icon_to_field
from bulma_forms.views import BulmaFormsMixin
from design.views.breadcrumbs import BreadcrumbMixin


class Login(BulmaFormsMixin, BreadcrumbMixin, auth_views.LoginView):
    page_title = _("Login")
    next_page = "home"
    template_name = "bulma_auth/login.html"
    form_submit_text = _("Log in")
    form_cancel_page = "home"

    def get_form(self, form_class=None):
        form: Form = super().get_form(form_class)
        add_icon_to_field(form, "username", "user")
        add_icon_to_field(form, "password", "lock")
        return form


class Logout(BreadcrumbMixin, auth_views.LogoutView):
    page_title = _("Logout")
    next_page = "home"


class PasswordChange(BulmaFormsMixin, BreadcrumbMixin, auth_views.PasswordChangeView):
    page_title = _("Change Password")
    template_name = "bulma_auth/password_change.html"
    form_submit_text = _("Change my password")
    form_cancel_page = "home"


class PasswordChangeDone(BreadcrumbMixin, auth_views.PasswordChangeDoneView):
    page_title = _("Successfully Changed Password")
    template_name = "bulma_auth/password_change_done.html"


class PasswordReset(BulmaFormsMixin, BreadcrumbMixin, auth_views.PasswordResetView):
    page_title = _("Forgotten your password?")
    from_email = "ErbslandFORMER <automation@erbsland.ch>"
    template_name = "bulma_auth/password_reset.html"
    form_submit_text = _("Reset my password")
    form_cancel_page = "home"


class PasswordResetConfirm(BulmaFormsMixin, BreadcrumbMixin, auth_views.PasswordResetConfirmView):
    page_title = _("Confirm Password Reset")
    template_name = "bulma_auth/password_confirm.html"
    form_submit_text = _("Change my Password")
    form_cancel_page = "home"


class PasswordResetDone(BreadcrumbMixin, auth_views.PasswordResetDoneView):
    page_title = _("Password Reset Email Sent")
    template_name = "bulma_auth/password_reset_done.html"


class PasswordResetComplete(BreadcrumbMixin, auth_views.PasswordResetCompleteView):
    page_title = _("Successfully Reset Password")
    template_name = "bulma_auth/password_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = _("Log in")
        context["button_url"] = reverse_lazy("login")
        return context
