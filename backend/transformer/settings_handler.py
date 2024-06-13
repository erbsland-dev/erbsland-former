#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Generic, Any

from django.core.exceptions import BadRequest
from django.http import HttpRequest
from django.utils.text import normalize_newlines
from django.utils.translation import gettext_lazy as _

from backend.tools.action_info import ActionInfo
from backend.tools.regular_expressions import RE_PLAIN_TEXT_INVALID
from backend.transformer.settings import TransformerSettingsBase
from design.views.action import ActionHandlerResponse

SettingsClass = TypeVar("SettingsClass", bound=TransformerSettingsBase)


class SettingsHandler(ABC, Generic[SettingsClass]):
    """
    The abstract interface for all settings-handler of a transformer implementation.

    Implement this class by implementing the abstract methods and add `handle_[action name]` methods to
    handle individual actions that are generated from your HTML template. In a such method, you have access
    to the variables `self.action_name`, `self.action_value`, `self.settings` and `self.request`.

    Before your handler is called, the `update_settings_from_request()` method is called, in which you
    have to update the `self.settings` object with the values from the submitted form.

    In your handler, you can further change contents of your `settings` instance. Depending on your return value,
    the surrounding handler will automatically save your changes in the settings object.

    - If you return `None`, the settings will be saved in the database and the page with the settings will
      be reloaded. Use this if a manipulation of the settings changes the displayed values, but it is likely that
      the user likes to make more edits.
    - If you return `SAVE_AND_CLOSE_RESPONSE`, the changes in the settings object will be saved and the interface
      returns to the list of transformer profiles, or back to the settings.
    - In case of any error, throw a `ValueError` or `HttpBadRequest` exception. In this case, changes on the
      settings object are not saved.
    """

    SAVE_AND_CLOSE_RESPONSE = "save_and_close"

    def __init__(self):
        """
        Initialize basic fields for the settings handler.
        """
        self.settings: Optional[SettingsClass] = None
        self.request: Optional[HttpRequest] = None
        self.action_name = ""
        self.action_value = ""

    @abstractmethod
    def get_class(self) -> Type[SettingsClass]:
        """
        Get the class that shall be used to store and handle the settings.

        :return: The generic `Settings` class or a derived class.
        """
        pass

    def get_settings_from_json(self, json_data: dict, version: int) -> SettingsClass:
        """
        Create an instance of a settings object from the given JSON data.

        :param json_data: The JSON data.
        :param version: The version of the transformer and therefore settings version.
        :return: A new settings object.
        """
        return self.get_class().from_json(json_data, version=version, verify_type=False)

    @abstractmethod
    def get_template(self) -> str:
        """
        Get the name/path of the template to be rendered for the settings.

        This template must contain a form that submits changes via POST request.
        The current settings are available to the template via `settings` variable. Alternatively
        you can add more variables by extending the `get_context()` method.
        """
        pass

    @abstractmethod
    def get_default(self) -> SettingsClass:
        """
        Create the default settings.
        """
        pass

    @abstractmethod
    def update_settings_from_request(self) -> None:
        """
        Implement this method to update the current `self.settings` object from the submitted request data.

        If the user presses any action button in the interface, this method is called before the handler
        in order to update the data stored in `self.settings`. Therefore, in your handler you already access
        the updated data and just have to apply the action to it.

        This is important as the user may change settings, then e.g. click on "Rename Profile", which is
        handled by the editor. In this case, the changes in the currently visible page must be preserved.

        The idea is to only preserve any changed data, but not execute any action yet.
        """
        pass

    def handle_save(self) -> ActionHandlerResponse:
        """
        Handle the case if the user clicks the "Save" button.

        By default, as the current settings are automatically saved using the `update_settings_from_request()` method
        this method does nothing and returns `None`.
        """
        return None

    def handle_save_and_close(self) -> ActionHandlerResponse:
        """
        Handle the case if the user clicks the "Save and Close" button.

        By default, as the current settings are automatically saved using the `update_settings_from_request()` method
        this method does nothing and returns the `SAVE_AND_CLOSE_RESPONSE`.
        """
        return self.SAVE_AND_CLOSE_RESPONSE

    def handle_unknown_action(self) -> ActionHandlerResponse:
        """
        By default, unknown actions result in an error message. Overwrite this method to handle them.
        """
        raise BadRequest("Unknown action")

    def get_context(self) -> dict:
        """
        Get the context variables for the template.

        The `self.request` and `self.settings` fields are set with the current request and settings instance.
        By default, the variable `settings` is added to the context.

        :return: A dictionary with the context variables.
        """
        return {
            "settings": self.settings,
            "card_list_actions": lambda: self.get_card_list_actions(),
        }

    def get_post_name_prefix(self) -> str:
        """
        Get the prefix that is added for all fields for the settings returned via POST.

        Overwrite to change the prefix.
        """
        return ""

    def get_post_value(self, name: str, default: Optional[str] = "", cast_type: Type = str) -> Any:
        """
        Get a settings value from the POST request.

        The settings forms are processed manually and not via Django forms. This method provides a common method
        to retrieve and cleaning the retrieved values if necessary. That's especially important for text fields.
        Text are also limited to a size of 100k of data – which is already an absurdly large amount of text –
        yet, this can be still handled gracefully by the application.

        :param name: The name of the field.
        :param default: An optional default value.
        :param cast_type: The expected type of the value.
        :return: The value of the field.
        """
        name_prefix = self.get_post_name_prefix()
        value = self.request.POST.get(f"{name_prefix}{name}", default)
        if cast_type is int:
            try:
                value = int(value)
            except ValueError:
                value = default
        elif cast_type is bool:
            value = bool(value)
        else:
            value = str(value)
        if isinstance(value, str):
            if len(value) > 100_000:
                value = value[:100_000]
            value = normalize_newlines(value)
            value = RE_PLAIN_TEXT_INVALID.sub("", value)
        return value

    def get_card_list_actions(self) -> list[ActionInfo]:
        """
        Get a list of card list action, added as `card_list_actions` to the render context.

        The idea is to normalize how actions in "card lists" are rendered to share as much code as possible
        between the transformer implementations.
        """
        return [
            ActionInfo(action_name="delete", title=_("Delete"), icon_name="trash", color_classes="has-text-danger"),
            ActionInfo(action_name="duplicate", title=_("Duplicate"), icon_name="copy"),
            ActionInfo(
                action_name="move_top", title=_("Move to Begin"), icon_name="arrows-up-to-line", disabled_if="first"
            ),
            ActionInfo(action_name="move_up", title=_("Move Up"), icon_name="arrow-up", disabled_if="first"),
            ActionInfo(action_name="move_down", title=_("Move Down"), icon_name="arrow-down", disabled_if="last"),
            ActionInfo(
                action_name="move_bottom", title=_("Move to End"), icon_name="arrows-down-to-line", disabled_if="last"
            ),
        ]
