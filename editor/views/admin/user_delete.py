#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from design.views.generic import DeleteView, AuthenticationLevel


class UserDeleteView(DeleteView):
    model = User
    authentication_level = AuthenticationLevel.SUPERUSER

    def get_success_url(self):
        return reverse_lazy("home")

    def get_warning_text(self) -> str:
        return (
            _(
                "Deleting users is not recommended! Please deactivate the users instead. "
                "If you click on “Delete User” below, the user “%(object_name)s” will be deleted "
                "irrecoverable. All data linked with this user will be deleted as well."
            )
            % self.text_replacements
        )

    def form_valid(self, form):
        # Checks to prevent disasters.
        if self.object.is_superuser:
            form.add_error(None, _("You must not delete a superuser!"))
            return self.form_invalid(form)
        if self.object.username == self.request.user.username:
            form.add_error(None, _("You must not delete your own user!"))
            return self.form_invalid(form)
        return super().form_valid(form)
