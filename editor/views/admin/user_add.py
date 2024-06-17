#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import secrets

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from design.views.breadcrumbs import Breadcrumb
from design.views.generic import FormView, AuthenticationLevel


class UserAddForm(forms.Form):

    username_validator = UnicodeUsernameValidator()

    username = forms.CharField(
        required=True,
        max_length=64,
        label=_("Username"),
        help_text=_("An unique username, with letters and numbers only."),
        validators=[username_validator],
        widget=forms.TextInput(attrs={"class": "is-family-monospace"}),
    )
    first_name = forms.CharField(
        max_length=150, label=_("First Name"), help_text=_("The first name of the user."), required=False
    )
    last_name = forms.CharField(
        max_length=150, label=_("Last Name"), help_text=_("The last name of the user."), required=False
    )
    email = forms.EmailField(
        required=True,
        label=_("Email address"),
        help_text=_("The email address of the user. Used for password resets."),
    )
    password = forms.CharField(
        required=True,
        max_length=150,
        label=_("Initial Password"),
        help_text=_("The initial password for the user. 16+ random characters."),
        validators=[validate_password],
        widget=forms.TextInput(attrs={"class": "is-family-monospace"}),
    )


class UserAddView(FormView):
    form = UserAddForm
    template_name = "editor/admin/user_add.html"
    authentication_level = AuthenticationLevel.ADMIN

    def get_form(self, form_class=None) -> UserAddForm:
        initial = None
        if self.request.method == "GET":
            initial = {
                "username": f"user_{secrets.token_hex(3)}",
                "password": secrets.token_urlsafe(32),
            }
        return UserAddForm(data=self.request.POST or None, initial=initial)

    def get_success_url(self) -> str:
        return reverse_lazy("home")

    def get_page_title(self) -> str:
        return _("Add New User")

    def get_form_submit_text(self) -> str:
        return _("Add New User")

    def get_form_submit_icon(self) -> str:
        return "plus"

    def get_form_cancel_text(self) -> str:
        return _("Back")

    def get_form_cancel_icon(self) -> str:
        return "arrow-left"

    def get_form_cancel_url(self) -> str:
        return reverse_lazy("home")

    def get_page_icon_name(self) -> str:
        return "user"

    def get_breadcrumbs_title(self) -> str:
        return _("Add")

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return [
            Breadcrumb(_("Administration"), reverse_lazy("admin_home")),
            Breadcrumb(_("User"), reverse_lazy("admin_home")),
        ]

    def create_user(self, form, *, is_staff: bool):
        with transaction.atomic():
            if User.objects.filter(username=form.cleaned_data["username"]).exists():
                form.add_error("username", _("Username already exists"))
                return self.form_invalid(form)
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.is_staff = is_staff
            user.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        return self.create_user(form, is_staff=False)
