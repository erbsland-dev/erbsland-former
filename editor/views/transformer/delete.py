#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend import models
from design.views.generic import DeleteView
from editor.views.transformer.access import TransformerAccessMixin


class TransformerDeleteView(TransformerAccessMixin, DeleteView):
    model = models.TransformerProfile
    success_url = reverse_lazy("transformer")

    def get_form_cancel_url(self) -> str:
        return reverse_lazy("transformer")

    def get_warning_text(self) -> str:
        return (
            _(
                "If you click on “Delete Transformer Profile” below, the profile “%(object_name)s” will be "
                "deleted irrecoverable. Yet, transformations you have done with this profile will stay intact, "
                "but they have no link to this profile anymore."
            )
            % self.text_replacements
        )
