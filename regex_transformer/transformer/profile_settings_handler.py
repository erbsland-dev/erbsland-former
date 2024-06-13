#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Type, Optional, Any

from django.contrib import messages
from django.core.exceptions import BadRequest
from django.utils.translation import gettext_lazy as _

from backend.transformer.settings_handler import SettingsHandler, SettingsClass
from design.views.action import ActionHandlerResponse
from regex_transformer.transformer.profile_settings import RegExProfileSettings


class RegExProfileSettingsHandler(SettingsHandler[RegExProfileSettings]):
    """
    Class to handle input from the profile settings page.
    """

    def get_class(self) -> Type[SettingsClass]:
        return RegExProfileSettings

    def get_template(self) -> str:
        return "regex_transformer/profile_settings.html"

    def get_default(self) -> SettingsClass:
        return RegExProfileSettings()

    def get_post_name_prefix(self) -> str:
        return "ret_"

    def _get_definition_value(self, name: str, index: int, cast_type: Type = str) -> Any:
        return self.get_post_value(f"definition.{index + 1}.{name}", cast_type=cast_type)

    def _update_definitions_from_submitted_data(self) -> None:
        # Manually process the inputs from the form.
        for index, definition in enumerate(self.settings.definitions):
            definition.pattern = self._get_definition_value("pattern", index)
            definition.assign_flags(lambda flag: self._get_definition_value(flag.name, index, cast_type=bool))
            definition.replacement = self._get_definition_value("replacement", index)

    def update_settings_from_request(self) -> None:
        self._update_definitions_from_submitted_data()

    def handle_add(self) -> ActionHandlerResponse:
        self.settings.add_definition()
        return None

    def _get_definition_index_from_action_value(self) -> int:
        """
        Get the definition index from the action value, or raise an exception if it is out of range.
        """
        try:
            index = int(self.action_value) - 1
            if index < 0 or index >= len(self.settings.definitions):
                raise BadRequest("Index out of range")
            return index
        except ValueError:
            raise BadRequest("Invalid action value")

    def handle_unknown_action(self) -> ActionHandlerResponse:
        definition_fn_name = f"handle_definition_{self.action_name}"
        if hasattr(self, definition_fn_name) and callable(getattr(self, definition_fn_name)):
            index = self._get_definition_index_from_action_value()
            getattr(self, definition_fn_name)(index)
            return None
        super().handle_unknown_action()

    def handle_definition_delete(self, index: int) -> None:
        del self.settings.definitions[index]
        messages.info(self.request, _("Deleted a definition."))

    def handle_definition_duplicate(self, index: int) -> None:
        definition_copy = self.settings.definitions[index].copy()
        self.settings.definitions.insert(index + 1, definition_copy)
        messages.info(self.request, _("Duplicated a definition."))

    def handle_definition_move_top(self, index: int) -> None:
        self.settings.definitions.insert(0, self.settings.definitions.pop(index))
        messages.info(self.request, _("Moved a definition."))

    def handle_definition_move_bottom(self, index: int) -> None:
        self.settings.definitions.append(self.settings.definitions.pop(index))
        messages.info(self.request, _("Moved a definition."))

    def handle_definition_move_up(self, index: int) -> None:
        if index > 0:
            self.settings.definitions[index], self.settings.definitions[index - 1] = (
                self.settings.definitions[index - 1],
                self.settings.definitions[index],
            )
            messages.info(self.request, _("Moved a definition."))

    def handle_definition_move_down(self, index: int) -> None:
        if index < len(self.settings.definitions) - 1:
            self.settings.definitions[index], self.settings.definitions[index + 1] = (
                self.settings.definitions[index + 1],
                self.settings.definitions[index],
            )
            messages.info(self.request, _("Moved a definition."))
