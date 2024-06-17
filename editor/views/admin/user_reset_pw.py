#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


from functools import cached_property

from django import forms
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from design.views.breadcrumbs import Breadcrumb
from design.views.generic import FormView, AuthenticationLevel


class UserResetPwForm(forms.Form):

    password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput, validators=[validate_password])
    password2 = forms.CharField(label=_("New Password Confirm"), widget=forms.PasswordInput)


class UserResetPwView(FormView):
    form = UserResetPwForm
    template_name = "editor/admin/user_reset_pw.html"
    authentication_level = AuthenticationLevel.ADMIN

    @cached_property
    def user(self):
        return User.objects.get(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("home")

    def get_form(self, form_class=None) -> UserResetPwForm:
        return UserResetPwForm(data=self.request.POST or None)

    def get_form_submit_text(self) -> str:
        return _("Reset Password")

    def get_form_submit_icon(self) -> str:
        return "save"

    def get_form_cancel_text(self) -> str:
        return _("Back")

    def get_form_cancel_icon(self) -> str:
        return "arrow-left"

    def get_form_cancel_url(self) -> str:
        return reverse_lazy("home")

    def get_page_title_prefix(self) -> str:
        if self.user.is_staff or self.user.is_superuser:
            return _("Reset Admin Password")
        return _("Reset User Password")

    def get_page_title(self) -> str:
        return self.user.username

    def get_page_icon_name(self) -> str:
        if self.user.is_staff or self.user.is_superuser:
            return "user-tie"
        return "user"

    def get_breadcrumbs_title(self) -> str:
        return self.user.username

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return [
            Breadcrumb(_("Administration"), reverse_lazy("admin_home")),
            Breadcrumb(_("User"), reverse_lazy("admin_home")),
        ]

    def is_form_submit_enabled(self) -> bool:
        if self.user.is_superuser and not self.request.user.is_superuser:
            return False
        if self.user.is_staff and not self.request.user.is_superuser:
            return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edited_user"] = self.user
        return context

    def form_valid(self, form):
        if self.user.is_superuser and not self.request.user.is_superuser:
            form.add_error(None, _("Only superusers can reset superusers passwords"))
            return self.form_invalid(form)
        if self.user.is_staff and not self.request.user.is_superuser:
            form.add_error(None, _("Only superusers can reset admin passwords"))
            return self.form_invalid(form)
        if form.cleaned_data["password1"] != form.cleaned_data["password2"]:
            form.add_error("password2", _("Passwords do not match"))
            return self.form_invalid(form)
        self.user.password = make_password(form.cleaned_data["password1"])
        self.user.save()
        messages.add_message(
            self.request,
            messages.WARNING,
            _("Password for user %(user_name)s successfully changed.") % {"user_name": self.user.username},
        )
        return HttpResponseRedirect(self.get_success_url())
