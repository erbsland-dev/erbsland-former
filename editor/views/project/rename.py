#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend import models
from design.views.generic import UpdateView
from editor.views.project import ProjectAccessMixin


class ProjectRenameForm(forms.ModelForm):
    cancel_icon = "arrow-left"

    class Meta:
        model = models.Project
        fields = ["name", "description"]


class ProjectRenameView(ProjectAccessMixin, UpdateView):
    model = models.TransformerProfile
    form_class = ProjectRenameForm
    template_name = "editor/project/rename.html"
    page_title_prefix = _("Rename")

    def get_success_url(self):
        return reverse("user_home")

    def get_form_submit_text(self) -> str:
        return _("Rename Project")

    def get_form_submit_icon(self) -> str:
        return "pen"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse("user_home")
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, _("Renamed project to “%(new_name)s”.") % {"new_name": form.cleaned_data["name"]}
        )
        return result
