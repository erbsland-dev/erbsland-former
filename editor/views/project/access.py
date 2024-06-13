#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    Http404,
    HttpResponseNotFound,
)
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend.models import Project, Revision
from backend.models.project_assistant import ProjectAssistant


class ProjectAccessMixin:
    """
    A mixin that provides and verifies access to a project.
    """

    def __init__(self, *args, **kwargs):
        self.request: Optional[HttpRequest] = None
        self.args: Optional[list] = None
        self.kwargs: Optional[dict] = None
        self._project: Optional[Project] = None
        self._revision: Optional[Revision] = None
        super().__init__(*args, **kwargs)

    def check_access_rights(self) -> Optional[HttpResponse]:
        """
        Test is the currently logged-in user has access to this project.
        """
        if not self.request.user or not self.request.user.is_authenticated:
            return HttpResponseForbidden("You don't have the required permission.")
        if not self.project.can_user_edit(self.request.user):
            return HttpResponseForbidden("You don't have the required permission.")
        return None

    def initialize_db_objects(self) -> Optional[HttpResponse]:
        """
        Initialize all database objects
        """
        try:
            self._project = self.get_project()
        except Project.DoesNotExist:
            return HttpResponseNotFound(_("The requested project was not found."))
        try:
            self._revision = self.get_revision()
        except Revision.DoesNotExist:
            return HttpResponseNotFound(_("The requested revision was not found in this project."))
        return None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if response := self.initialize_db_objects():
            return response
        if response := self.check_access_rights():
            return response
        return super().dispatch(request, *args, **kwargs)

    def get_project(self) -> Project:
        return Project.objects.get(pk=self.kwargs["pk"])

    def get_project_url(self) -> str:
        if not self.revision.is_latest:
            return reverse("project", kwargs={"pk": self.project.pk, "revision": self.revision.number})
        return reverse("project", kwargs={"pk": self.project.pk})

    def get_revision(self) -> Revision:
        revision_number = 0
        try:
            if "revision" in self.kwargs:
                revision_number = int(self.kwargs["revision"])
            elif "revision" in self.request.GET:
                revision_number = int(self.request.GET.get("revision", 0))
        except ValueError:
            raise Http404("The given revision number has the wrong format.")
        if revision_number > 0:
            try:
                return self.project.revisions.get(number=revision_number)
            except ObjectDoesNotExist:
                raise Http404("There is no such revision.")
        return self.project.get_latest_revision()

    def get_page_title(self) -> str:
        return self.project.name

    @property
    def project(self) -> Project:
        return self._project

    @property
    def revision(self) -> Revision:
        return self._revision

    @cached_property
    def is_latest_revision(self) -> bool:
        return self.revision.is_latest

    @cached_property
    def revision_count(self) -> int:
        return self.project.revisions.count()

    @cached_property
    def has_assistant(self) -> bool:
        return self.project.has_running_assistant()

    @cached_property
    def assistant(self) -> Optional[ProjectAssistant]:
        return self.project.get_running_assistant()

    @cached_property
    def is_own_assistant(self) -> bool:
        if self.has_assistant:
            return self.assistant.user == self.request.user
        return False

    @cached_property
    def has_unfinished_tasks(self) -> bool:
        return self.project.has_unfinished_tasks() or self.has_assistant

    def get_object(self, queryset=None):
        # Replace the get object method for project access subclasses.
        # It always returns the project.
        return self.project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        can_be_edited = not (self.has_unfinished_tasks or self.has_assistant)
        context.update(
            {
                "project": self.project,
                "revision": self.revision,
                "revision_count": lambda: self.revision_count,
                "is_latest_revision": self.is_latest_revision,
                "assistant": self.assistant,
                "is_own_assistant": self.is_own_assistant,
                "has_unfinished_tasks": self.has_unfinished_tasks,
                "can_be_edited": can_be_edited,
            }
        )
        if self.has_assistant:
            context["assistant_name"] = self.assistant.get_verbose_assistant_name()
            if self.assistant.user == self.request.user:
                context["assistant_user"] = _("you")
            else:
                context["assistant_user"] = _("user %(user)s") % {"user": self.assistant.user.username}
            context["assistant_stop_url"] = reverse_lazy(
                f"{self.assistant.assistant_name}_stop", kwargs={"pk": self.project.pk}
            )
            context["assistant_continue_url"] = reverse_lazy(
                f"{self.assistant.assistant_name}", kwargs={"pk": self.project.pk}
            )
        return context
