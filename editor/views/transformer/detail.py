#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Callable, Optional

from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend import models
from backend.transformer.settings_handler import SettingsHandler
from design.views.action import ActionDetailView, ActionHandlerResponse
from editor.views.transformer.access import TransformerAccessMixin


class TransformerDetailView(TransformerAccessMixin, ActionDetailView):
    """
    The detail view to display and edit the transformer settings.
    """

    page_title_prefix = _("Transformer Profile")
    model = models.Project
    template_name = "editor/transformer/detail.html"

    def get_page_title(self) -> str:
        return self.object.profile_name

    def get_page_icon_name(self) -> str:
        return self.transformer_profile.transformer.get_icon_name()

    def handle_rename_profile(self) -> ActionHandlerResponse:
        """
        Called if the user wants to rename the transformer profile.
        """
        settings_handler = self.get_settings_handler()
        settings_handler.update_settings_from_request()
        self.object.update_settings(settings_handler.settings)
        return reverse("transformer_rename", kwargs={"pk": self.transformer_profile.pk})

    def handle_unknown_action(self) -> ActionHandlerResponse:
        """
        All unknown actions are forwarded to the handler for the transformer profile.
        """
        settings_handler = self.get_settings_handler()
        settings_handler.update_settings_from_request()
        action_handler = self._get_action_handler(settings_handler)
        if action_handler:
            result = action_handler()
        else:
            result = settings_handler.handle_unknown_action()
        # If the handler returns a `HttpResponse`, do not save the settings.
        if isinstance(result, HttpResponse) and result.status_code != 200:
            return result
        self.object.update_settings(settings_handler.settings)
        if result == SettingsHandler.SAVE_AND_CLOSE_RESPONSE:
            messages.success(
                self.request,
                _("Successfully saved the changes in transformer profile “%(profile_name)s”.")
                % {"profile_name": self.object.profile_name},
            )
            return reverse("transformer")
        return result

    def _get_action_handler(self, settings_handler: SettingsHandler) -> Optional[Callable[[], ActionHandlerResponse]]:
        action_handler_name = f"handle_{self.action_name}"
        if hasattr(settings_handler, action_handler_name):
            method = getattr(settings_handler, action_handler_name)
            if not callable(method):
                raise ValueError(f"The attribute {action_handler_name} must be a callable method.")
            return method
        return None

    def get_settings_handler(self) -> SettingsHandler:
        handler = self.transformer_profile.transformer.profile_settings_handler
        handler.action_name = self.action_name
        handler.action_value = self.action_value
        handler.settings = self.transformer_profile.get_settings()
        handler.request = self.request
        return handler

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_handler = self.get_settings_handler()
        context.update(settings_handler.get_context())
        context["settings_template"] = settings_handler.get_template()
        return context
