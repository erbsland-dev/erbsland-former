#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import QuerySet
from django.urls import reverse

from backend.models import TransformerProfile
from design.views.action import ActionPageView, ActionHandlerResponse
from design.views.breadcrumbs import Breadcrumb
from design.views.generic import PageView
from django.utils.translation import gettext_lazy as _


class TransformerListView(LoginRequiredMixin, ActionPageView):
    """
    A view displaying a list with all transformers created by the current user.
    """

    page_title = _("Transformer Profiles")
    page_icon_name = "magic-wand-sparkles"
    template_name = "editor/transformer/list.html"

    def get_transformer_list(self) -> QuerySet[TransformerProfile]:
        return self.request.user.transformer_profiles.order_by("-modified")

    def handle_edit(self) -> ActionHandlerResponse:
        return reverse("transformer_edit", kwargs={"pk": self.action_value})

    def handle_delete(self) -> ActionHandlerResponse:
        return reverse("transformer_delete", kwargs={"pk": self.action_value})

    def handle_rename(self) -> ActionHandlerResponse:
        return reverse("transformer_rename", kwargs={"pk": self.action_value})

    def handle_duplicate(self) -> ActionHandlerResponse:
        with transaction.atomic():
            transformer = TransformerProfile.objects.get(pk=int(self.action_value))
            transformer.duplicate()
        return None

    def is_settings_page(self):
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transformer_list = self.get_transformer_list()
        context.update(
            {
                "transformer_list": transformer_list,
                "has_transformers": transformer_list.count() > 0,
                "has_no_transformers": transformer_list.count() == 0,
            }
        )
        return context
