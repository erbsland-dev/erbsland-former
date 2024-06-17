#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from design.views.action import ActionPageView, ActionHandlerResponse
from design.views.breadcrumbs import Breadcrumb

from design.views.generic import AuthenticationLevel


class AdminHomeView(ActionPageView):
    """
    The home view for the administration.
    """

    template_name = "editor/admin/home.html"
    login_url = reverse_lazy("home")
    authentication_level = AuthenticationLevel.ADMIN

    def get_page_title(self) -> str:
        return _("Administration")

    def get_page_icon_name(self) -> str:
        return "users"

    def change_user_active(self, *, is_active: bool) -> User:
        with transaction.atomic():
            edited_user = User.objects.get(pk=self.action_value)
            if edited_user.is_staff and not self.request.user.is_superuser:
                return None  # Ignore
            edited_user.is_active = is_active
            edited_user.save()
            return edited_user

    def handle_user_make_inactive(self) -> ActionHandlerResponse:
        edited_user = self.change_user_active(is_active=False)
        messages.add_message(
            self.request,
            messages.WARNING,
            _("Successfully set user “%(user_name)s” inactive.") % {"user_name": edited_user.username},
        )
        return None

    def handle_user_make_active(self) -> ActionHandlerResponse:
        edited_user = self.change_user_active(is_active=True)
        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Successfully set user “%(user_name)s” active.") % {"user_name": edited_user.username},
        )
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            users = User.objects.order_by("-is_active", "username")
        else:
            users = User.objects.filter(is_superuser=False).order_by("-is_active", "username")
        context["users"] = users
        return context
