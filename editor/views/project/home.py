#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _

from design.views.action import ActionPageView, ActionHandlerResponse
from backend.models import Project


class UserHome(ActionPageView):
    """
    The root page of the application, displaying a list of projects.
    """

    template_name = "editor/project/list.html"
    login_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return HttpResponseRedirect(reverse_lazy("admin_home"))
        return super().dispatch(request, *args, **kwargs)

    def handle_delete(self) -> ActionHandlerResponse:
        return reverse("project_delete", kwargs={"pk": self.action_value})

    def handle_edit(self) -> ActionHandlerResponse:
        return reverse("project", kwargs={"pk": self.action_value})

    def handle_rename(self) -> ActionHandlerResponse:
        return reverse("project_rename", kwargs={"pk": self.action_value})

    def get_page_title(self) -> str:
        return _("Projects")

    def get_breadcrumbs_title(self) -> str:
        return _("Projects")

    def get_page_icon_name(self) -> str:
        return "folder-tree"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = Project.objects.filter(owner_id=self.request.user.id).order_by("-modified")
        context["projects"] = projects
        context["has_projects"] = projects.count() > 0
        context["has_no_projects"] = projects.count() == 0
        return context
