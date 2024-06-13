#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from abc import abstractmethod, ABCMeta
from functools import cached_property
from typing import Optional, TypeVar, Type

from backend.tools.extension import Extension, ExtensionMeta
from backend.tools.statistic.statistic_field import StatisticField
from backend.transformer.processor import Processor, UserSettings, ProfileSettings
from backend.transformer.settings import TransformerSettingsBase
from backend.transformer.settings_handler import SettingsHandler
from tasks.actions.status import TaskStatusField

ProcessorClass = TypeVar("ProcessorClass", bound=Processor)


class TransformerMeta(ExtensionMeta):
    """
    A custom metaclass for the transformer case, to make sure is implemented correctly.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        # Classes that have a `Base` suffix must not (yet) comply to these rules.
        if not cls.__name__.endswith("Base"):
            for class_variable in ["profile_settings_class", "processor_class"]:
                value = namespace.get(class_variable, "")
                if not isinstance(value, type):
                    raise TypeError(f"{cls.__name__} must define a class using the '{class_variable}' class variable!")
        return cls


class TransformerBase(Extension, metaclass=TransformerMeta):
    """
    This is the baseclass for all registered transformers for the system.
    """

    description = ""
    """A short description of the transformer."""

    version: int = 1
    """The version of the transformer."""

    profile_settings_class: Type[ProfileSettings] = None
    """The class for the profile settings."""

    user_settings_class: Type[UserSettings] = None
    """The class for the user settings."""

    processor_class: Type[ProcessorClass] = None
    """The class for the processor of this transformer."""

    icon_name: str = None
    """An icon name to be displayed in transformer profiles."""

    title_background_color_class: str = None
    """A background color class, to colorize the title of transformer profiles."""

    short_name: str = ""
    """A short name to be displayed in front of the icon. 3-5 letters."""

    status_fields: list[TaskStatusField] = []
    """A list of additional task status fields for this transformer."""

    statistic_fields: list[StatisticField] = []
    """A list of additional statistic fields for this transformer."""

    def get_description(self) -> str:
        """
        Get the description for this transformer.
        """
        return self.description

    def get_version(self) -> int:
        """
        Get the version of this transformer.
        """
        return self.version

    def get_icon_name(self) -> str:
        """
        Get the icon name for this transformer.
        """
        if not self.icon_name:
            return "magic-wand-sparkles"
        return self.icon_name

    def get_title_background_color_class(self) -> str:
        """
        Get the background class for the title in cards.
        This must be a dark background that contrasts with white text.
        """
        if not self.title_background_color_class:
            return "has-background-dark"
        return self.title_background_color_class

    def get_short_name(self) -> str:
        """
        Get the short name for this transformer.
        """
        return self.short_name

    def get_status_fields(self) -> list[TaskStatusField]:
        """
        Get the status fields for this transformer.
        """
        return self.status_fields

    def get_statistic_fields(self) -> list[StatisticField]:
        """
        Get the statistic fields for this transformer.
        """
        return self.statistic_fields

    def get_profile_settings_class(self) -> Type[ProfileSettings]:
        """
        Get the class for the profile settings.
        """
        return self.profile_settings_class

    def get_user_settings_class(self) -> Type[UserSettings]:
        """
        Get the class for the user settings.
        """
        return self.user_settings_class

    def get_processor_class(self) -> Type[ProcessorClass]:
        """
        Get the processor class.
        """
        return self.processor_class

    @cached_property
    def profile_settings_handler(self) -> SettingsHandler:
        """
        The profile settings handler.
        """
        profile_settings_class = self.get_profile_settings_class()
        return profile_settings_class()

    @cached_property
    def user_settings_handler(self) -> Optional[SettingsHandler]:
        """
        The optional user settings handler.
        """
        user_settings_class = self.get_user_settings_class()
        if user_settings_class is None:
            return None
        return user_settings_class()

    def create_processor(
        self,
        task_id: str,
        profile_settings: TransformerSettingsBase,
        user_settings: Optional[TransformerSettingsBase] = None,
    ) -> Processor:
        """
        Create a new processor for this transformer.

        :param task_id: The task id that is assigned to the running transformation.
        :param profile_settings: The profile settings for the transformer.
        :param user_settings: Optional user settings.
        :return: A new instance of the content processor.
        """
        processor_class = self.get_processor_class()
        return processor_class(task_id, profile_settings, user_settings)
