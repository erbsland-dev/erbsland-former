#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property

from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from design.views.breadcrumbs import Breadcrumb
from design.views.generic import FormView, AuthenticationLevel


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]
        help_texts = {"username": ""}


class UserEditView(FormView):
    form = UserEditForm
    template_name = "editor/admin/user_edit.html"
    authentication_level = AuthenticationLevel.ADMIN

    @cached_property
    def user(self):
        return User.objects.get(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("home")

    def get_form(self, form_class=None) -> UserEditForm:
        return UserEditForm(data=self.request.POST or None, instance=self.user)

    def get_form_submit_text(self) -> str:
        return _("Save and Close")

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
            return _("Admin")
        return _("User")

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edited_user"] = self.user
        return context

    def is_form_submit_enabled(self) -> bool:
        if self.user.is_superuser and not self.request.user.is_superuser:
            return False
        if self.user.is_staff and not self.request.user.is_superuser:
            return False
        return True

    def form_valid(self, form):
        if self.user.is_superuser and not self.request.user.is_superuser:
            form.add_error(None, _("Only superusers can edit superusers"))
            return self.form_invalid(form)
        if self.user.is_staff and not self.request.user.is_superuser:
            form.add_error(None, _("Only superusers can edit admins"))
            return self.form_invalid(form)
        form.save()
        messages.add_message(
            self.request,
            messages.INFO,
            _("User details for “%(user_name)s” successfully changed.") % {"user_name": self.user.username},
        )
        return HttpResponseRedirect(self.get_success_url())
