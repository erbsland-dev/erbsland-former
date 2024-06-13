#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from design.views.generic import PageView
from backend.models import Project


class Home(LoginRequiredMixin, PageView):
    """
    The root page of the application.
    """

    login_url = reverse_lazy("welcome")
    page_title = _("Projects")
    page_icon_name = "magic-wand-sparkles"
    template_name = "editor/home.html"

    def is_home(self) -> bool:
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = Project.objects.filter(owner_id=self.request.user.id).order_by("-modified")
        context["projects"] = projects
        context["has_projects"] = projects.count() > 0
        context["has_no_projects"] = projects.count() == 0
        return context


class Welcome(PageView):
    """
    The welcome view is displayed for users that aren't logged in but access the home view.
    Only for the home page, this is the better alternative than just displaying a non-descriptive login page.
    """

    page_title = _("Welcome")
    template_name = "editor/welcome.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy("home"))
        return super().get(request, *args, **kwargs)
