#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend import models
from design.views.generic import DeleteView
from editor.views.project import ProjectAccessMixin


class RevisionDeleteView(ProjectAccessMixin, DeleteView):
    model = models.Revision

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
        return _("Delete")

    def get_object(self, queryset=None):
        return self.revision

    def get_form_submit_text(self) -> str:
        return _("Delete Revision")

    def get_warning_text(self) -> str:
        return _(
            "If you click on the “Delete Revision” button below, the revision %(object_name)s of project "
            "“%(project_name)s” will be deleted irrecoverable. "
            "With the revision, all documents and its changes will be deleted as well."
        ) % {**self.text_replacements, "project_name": self.project.name}

    def form_valid(self, form):
        success_url = self.get_success_url()
        with transaction.atomic():
            if self.revision.successors.exists():
                # Cancel the operation of the revision has successors.
                return HttpResponseRedirect(self.get_form_cancel_url())
            is_latest_revision = self.revision.is_latest
            self.revision.delete()
            if is_latest_revision:
                new_latest_revision = self.project.revisions.order_by("-number").first()
                new_latest_revision.is_latest = True
                new_latest_revision.save()
        return HttpResponseRedirect(success_url)
