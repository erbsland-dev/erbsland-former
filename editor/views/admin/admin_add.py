#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import secrets

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from design.views.breadcrumbs import Breadcrumb
from design.views.generic import AuthenticationLevel
from editor.views.admin.user_add import UserAddForm, UserAddView


class AdminAddForm(UserAddForm):
    pass


class AdminAddView(UserAddView):
    form = AdminAddForm
    template_name = "editor/admin/admin_add.html"
    authentication_level = AuthenticationLevel.SUPERUSER

    def get_form(self, form_class=None) -> UserAddForm:
        initial = None
        if self.request.method == "GET":
            initial = {
                "username": f"admin_{secrets.token_hex(3)}",
                "password": secrets.token_urlsafe(32),
            }
        return UserAddForm(data=self.request.POST or None, initial=initial)

    def get_page_title(self) -> str:
        return _("Add New Admin")

    def get_form_submit_text(self) -> str:
        return _("Add New Admin")

    def get_page_icon_name(self) -> str:
        return "user-tie"

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return [Breadcrumb(_("User"), reverse_lazy("home"))]

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            form.add_error(None, _("Only superusers can create admin users."))
            return self.form_invalid(form)
        return self.create_user(form, is_staff=True)
