#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import datetime

from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend import models
from backend.syntax_handler import syntax_manager
from design.views.breadcrumbs import Breadcrumb
from design.views.generic import CreateView


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ["name", "description", "default_syntax"]
        help_texts = {
            "default_syntax": _("Select the primary syntax to be used for the documents in this project."),
            "name": _("Please select a unique and concise name for your new project."),
            "description": _("You have the option to include a brief description of the project."),
        }
        labels = {
            "name": _("Project Name"),
            "description": _("Brief Description"),
            "default_syntax": _("Primary Document Syntax"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].initial = _("My Project %(timestamp)s") % {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.fields["default_syntax"].widget = forms.Select(choices=syntax_manager.get_choices())
        self.fields["default_syntax"].initial = syntax_manager.get_default_name()


class ProjectCreateView(CreateView):
    model = models.Project
    form_class = ProjectCreateForm
    page_title = _("Add New Project")
    breadcrumbs_title = _("Add")
    template_name = "editor/project/create.html"

    def get_success_url(self):
        return reverse("project", kwargs={"pk": self.object.pk})

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return [Breadcrumb(_("Projects"), reverse_lazy("user_home"))]

    def form_valid(self, form: forms.Form):
        # Manually create the project using the manager
        self.object = models.Project.objects.create_project(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            owner=self.request.user,
            default_syntax=form.cleaned_data["default_syntax"],
        )
        return HttpResponseRedirect(self.get_success_url())
