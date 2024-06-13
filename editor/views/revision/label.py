#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend import models
from design.views.generic import UpdateView
from editor.views.project import ProjectAccessMixin


class RevisionEditLabelForm(forms.ModelForm):
    """
    A custom form edit the label of the revision.
    """

    class Meta:
        model = models.Revision
        fields = ["label"]


class RevisionEditLabelView(ProjectAccessMixin, UpdateView):
    model = models.Revision
    fields = ["label"]
    template_name = "design/modal/form.html"

    def get_success_url(self):
        # After deleting a revision, jump to the latest one in the project.
        return reverse_lazy("project", kwargs={"pk": self.project.pk})

    def get_form_cancel_url(self) -> str:
        return self.get_project_url()

    def get_page_title(self) -> str:
        return _("“%(project_name)s” Revision %(revision_number)d") % {
            "project_name": self.project.name,
            "revision_number": self.revision.number,
        }

    def get_page_title_prefix(self) -> str:
        return _("Edit Label")

    def get_object(self, queryset=None):
        return self.revision
