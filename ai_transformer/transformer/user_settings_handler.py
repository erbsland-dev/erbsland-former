#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Type

from backend.transformer.settings_handler import SettingsHandler, SettingsClass
from ai_transformer.transformer.user_settings import AiUserSettings


class AiUserSettingsHandler(SettingsHandler[AiUserSettings]):
    """
    Class to handle the user settings.
    """

    def get_class(self) -> Type[SettingsClass]:
        return AiUserSettings

    def get_template(self) -> str:
        return "ai_transformer/user_settings.html"

    def get_default(self) -> SettingsClass:
        return AiUserSettings()

    def update_settings_from_request(self) -> None:
        self.settings.api_key.text = self.request.POST.get("ai_api_key", "")
        self.settings.organization_id = self.request.POST.get("ai_organization_id", "")
        self.settings.project_id = self.request.POST.get("ai_project_id", "")
