#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend import models
from design.views.generic import DeleteView
from editor.views.project import ProjectAccessMixin


class ProjectDeleteView(ProjectAccessMixin, DeleteView):
    model = models.Project
    success_url = reverse_lazy("home")

    def get_warning_text(self) -> str:
        return (
            _(
                "If you click on “Delete Project” below, the project “%(object_name)s” will be deleted "
                "irrecoverable. With the project, all documents and revisions will be deleted as well."
            )
            % self.text_replacements
        )
