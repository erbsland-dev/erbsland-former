#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from design.views.generic import FormView, MessageView
from editor.views.project import ProjectAccessMixin


class ProjectCannotEditView(ProjectAccessMixin, FormView):
    template_name = "editor/project/cannot_edit.html"

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if not next_url:
            next_url = reverse("project", kwargs={"pk": self.kwargs["pk"]})
        return next_url


class ProjectNoPendingFragments(ProjectAccessMixin, MessageView):
    message_text = _("All done! There are no pending fragments left in this project.")
    form_submit_text = _("Back to Project")

    def get_page_title(self) -> str:
        return _("Done!")

    def get_success_url(self):
        return reverse("project", kwargs={"pk": self.kwargs["pk"]})


class ProjectNoRejectedFragments(ProjectAccessMixin, MessageView):
    message_text = _("All done! There are no rejected fragments left in this project.")
    form_submit_text = _("Back to Project")

    def get_page_title(self) -> str:
        return _("Done!")

    def get_success_url(self):
        return reverse("project", kwargs={"pk": self.kwargs["pk"]})
