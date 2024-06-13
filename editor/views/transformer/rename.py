#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend import models
from design.views.generic import UpdateView
from editor.views.transformer.access import TransformerAccessMixin


class TransformerRenameForm(forms.ModelForm):
    submit_text = _("Rename")
    submit_icon = "edit"
    cancel_icon = "arrow-left"

    class Meta:
        model = models.TransformerProfile
        fields = ["profile_name"]


class TransformerRenameView(TransformerAccessMixin, UpdateView):
    model = models.TransformerProfile
    form_class = TransformerRenameForm
    template_name = "editor/transformer/rename.html"
    page_title_prefix = _("Rename")

    def get_success_url(self):
        return reverse("transformer_edit", kwargs={"pk": self.transformer_profile.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse("transformer_edit", kwargs={"pk": self.transformer_profile.pk})
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, _("Renamed profile to “%(new_name)s”.") % {"new_name": form.cleaned_data["profile_name"]}
        )
        return result
