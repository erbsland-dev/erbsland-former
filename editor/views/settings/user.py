#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Callable

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend.models import TransformerUserSettings
from backend.transformer import TransformerBase
from backend.transformer.manager import transformer_manager
from backend.transformer.settings import TransformerSettingsBase
from backend.transformer.settings_handler import SettingsHandler
from design.views.action import ActionPageView, ActionHandlerResponse
from design.views.breadcrumbs import Breadcrumb
from design.views.generic import PageView


class SettingPageType(enum.StrEnum):
    """
    The type of setting page.
    """

    TRANSFORMER = "transformer"


@dataclass
class SettingPage:
    """
    Details for a setting page.
    """

    name: str
    verbose_name: str
    type: SettingPageType


class UserSettingsView(ActionPageView):
    """
    The view to display and manager the user settings.
    """

    template_name = "editor/settings/user.html"
    page_title = _("User Settings")
    page_icon_name = "gear"

    @cached_property
    def setting_pages(self) -> list[SettingPage]:
        setting_pages: list[SettingPage] = []
        for transformer_name in transformer_manager.extension_names:
            transformer: TransformerBase = transformer_manager.get_extension(transformer_name)
            if transformer.user_settings_class:
                setting_pages.append(
                    SettingPage(
                        name=transformer_name,
                        verbose_name=transformer.get_verbose_name(),
                        type=SettingPageType.TRANSFORMER,
                    )
                )
        return setting_pages

    @cached_property
    def default_setting_page(self) -> SettingPage:
        return self.setting_pages[0]

    @cached_property
    def selected_setting_page(self) -> Optional[SettingPage]:
        if not self.setting_pages:
            return None
        name = self.kwargs.get("setting_page", self.default_setting_page.name)
        return next((page for page in self.setting_pages if page.name == name), self.default_setting_page)

    def dispatch(self, request, *args, **kwargs):
        setting_page = self.kwargs.get("setting_page", "")
        if not setting_page or (setting_page and not any(page.name == setting_page for page in self.setting_pages)):
            return redirect(reverse("user_settings", kwargs={"setting_page": self.default_setting_page.name}))
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def selected_setting_page_name(self) -> str:
        if self.selected_setting_page:
            setting_page_name = self.selected_setting_page.name
        else:
            setting_page_name = ""
        return setting_page_name

    @cached_property
    def selected_setting_template(self) -> str:
        page = self.selected_setting_page
        if not page:
            return ""
        if page.type == SettingPageType.TRANSFORMER:
            transformer: TransformerBase = transformer_manager.get_extension(page.name)
            return transformer.user_settings_handler.get_template()
        return ""

    def get_page_title(self) -> str:
        if not self.selected_setting_page:
            return _("User Settings")
        return self.selected_setting_page.verbose_name

    def get_page_title_prefix(self) -> str:
        if not self.selected_setting_page:
            return ""
        return _("User Settings")

    def get_breadcrumbs_title(self) -> str:
        if not self.selected_setting_page:
            return _("User Settings")
        return self.selected_setting_page.verbose_name

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        if not self.selected_setting_page:
            return []
        return [Breadcrumb(_("User Settings"), reverse_lazy("user_settings"))]

    def get_settings_object(self) -> TransformerUserSettings:
        return TransformerUserSettings.objects.get_or_create_default(self.request.user, self.selected_setting_page_name)

    def get_settings_handler(self) -> SettingsHandler:
        settings_obj = self.get_settings_object()
        handler = settings_obj.transformer.user_settings_handler
        handler.settings = settings_obj.get_settings()
        handler.action_name = self.action_name
        handler.action_value = self.action_value
        handler.request = self.request
        return handler

    def _get_action_handler(self, settings_handler: SettingsHandler) -> Optional[Callable[[], ActionHandlerResponse]]:
        action_handler_name = f"handle_{self.action_name}"
        if hasattr(settings_handler, action_handler_name):
            method = getattr(settings_handler, action_handler_name)
            if not callable(method):
                raise ValueError(f"The attribute {action_handler_name} must be a callable method.")
            return method
        return None

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
        # Save all settings in the database.
        settings_obj = self.get_settings_object()
        settings_obj.update_settings(settings_handler.settings)
        if result == SettingsHandler.SAVE_AND_CLOSE_RESPONSE:
            return reverse("home")
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "setting_pages": self.setting_pages,
                "selected_setting_page": self.selected_setting_page_name,
                "selected_setting_template": self.selected_setting_template,
            }
        )
        settings_handler = self.get_settings_handler()
        context.update(settings_handler.get_context())
        return context
