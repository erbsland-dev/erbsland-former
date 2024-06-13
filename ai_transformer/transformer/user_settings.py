#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.conf import settings

from backend.tools.settings_encryption.string import EncryptedString
from backend.transformer.settings import TransformerSettingsBase


class AiUserSettings(TransformerSettingsBase):
    """
    The user settings object for AI Transformer.
    """

    serialized_classes = [EncryptedString]

    def __init__(self):
        self.api_key = EncryptedString()  # The encrypted API key
        self.organization_id: str = ""  # The organization identifier
        self.project_id: str = ""  # The project identifier.

    @property
    def user_overrides_allowed(self) -> bool:
        return settings.AI_ALLOW_USER_OVERRIDES

    @property
    def has_server_api_key(self) -> bool:
        return settings.AI_API_KEY != ""

    @property
    def has_server_organization_id(self) -> bool:
        return settings.AI_API_KEY != ""

    @property
    def has_server_project_id(self) -> bool:
        return settings.AI_API_KEY != ""

    def get_api_key(self) -> str:
        result = settings.AI_API_KEY
        if self.user_overrides_allowed and self.api_key.text:
            result = self.api_key.text
        return result

    def get_organization_id(self) -> str:
        result = settings.AI_ORGANIZATION_ID
        if self.user_overrides_allowed and self.organization_id:
            result = self.organization_id
        return result

    def get_project_id(self) -> str:
        result = settings.AI_PROJECT_ID
        if self.user_overrides_allowed and self.project_id:
            result = self.project_id
        return result
