#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from design.views.generic import DesignMixin


class Welcome(DesignMixin, TemplateView):
    """
    The welcome view is displayed for users that aren't logged in.

    For authenticated users, this view redirects to the user or admin home view.
    """

    page_title = _("Welcome")
    template_name = "editor/welcome.html"

    def is_home(self) -> bool:
        return True

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser or self.request.user.is_staff:
                return redirect(reverse_lazy("admin_home"))
            else:
                return redirect(reverse_lazy("user_home"))
        return super().get(request, *args, **kwargs)
