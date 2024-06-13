#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import datetime

from django import forms
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _

from backend.models import TransformerProfile
from backend.transformer import TransformerBase
from backend.transformer.manager import transformer_manager
from design.views.breadcrumbs import Breadcrumb
from design.views.generic import CreateView


class TransformerCreateForm(forms.ModelForm):
    submit_text = _("Add Transformer Profile")
    submit_icon = "plus"
    cancel_icon = "arrow-left"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_name"].initial = _("My Transformer %(timestamp)s") % {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.fields["transformer_name"].widget = forms.Select(choices=transformer_manager.get_choices())
        self.fields["transformer_name"].initial = transformer_manager.get_default_name()
        self.fields["description"].widget = forms.Textarea(attrs={"rows": 3})

    class Meta:
        model = TransformerProfile
        fields = ["profile_name", "transformer_name", "description"]
        help_texts = {
            "profile_name": _("Enter a short and unique for this transformer profile."),
            "transformer_name": _("Select the type of transformer you like to use."),
            "description": _("Add optional notes."),
        }


class TransformerCreateView(CreateView):
    """
    A view to add a new transformer to the list.
    """

    model = TransformerProfile
    form_class = TransformerCreateForm
    template_name = "editor/transformer/create.html"
    page_icon_name = "magic-wand-sparkles"
    page_title = _("Add New Transformer Profile")
    breadcrumbs_title = _("Add")

    def get_success_url(self):
        return reverse("transformer_edit", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        transformer: TransformerBase = transformer_manager.get_transformer(form.instance.transformer_name)
        version = transformer.get_version()
        form.instance.owner = self.request.user
        form.instance.version = version
        form.instance.configuration = transformer.profile_settings_handler.get_default().to_json()
        return super().form_valid(form)

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return [Breadcrumb(_("Transformer Profiles"), reverse("transformer"))]
