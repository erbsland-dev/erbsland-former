#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend import models
from design.views.generic import DeleteView
from editor.views.fragment.access import FragmentAccessMixin


class DeleteEditView(FragmentAccessMixin, DeleteView):
    model = models.Fragment
    form_submit_text = _("Delete Edit")

    def get_form_success_url(self):
        return reverse("fragment", kwargs={"pk": self.object.pk})

    def get_form_cancel_url(self):
        return self.get_form_success_url()

    def get_page_title_prefix(self) -> str:
        return ""

    def get_page_title(self):
        return _("Delete the Fragment Edit?")

    def get_warning_text(self) -> str:
        return _(
            "If you click on “Delete Edit” your manual edit of this fragment is deleted. "
            "The fragment itself and any transformation results stay intact. Be aware that the deleted edit "
            "cannot be recovered."
        )

    def form_valid(self, form):
        with transaction.atomic():
            fragment = self.get_fragment()
            success_url = self.get_success_url()
            if not fragment.has_edit:
                return
            fragment.delete_edit()
            return HttpResponseRedirect(success_url)
