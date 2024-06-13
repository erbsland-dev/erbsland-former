#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import importlib
import logging
from functools import cache
from typing import Union

from django.utils.functional import LazyObject

from tasks.actions.base import ActionBase
from tasks.actions.status import TaskStatusField

logger = logging.getLogger(__name__)


class ActionManager:
    """
    The manager for all registered actions.
    """

    def __init__(self):
        from django.apps import apps

        if not apps.ready:
            raise ValueError("Action manager is initialized too early, before all apps are ready.")
        self._registered_actions: dict[str, type[ActionBase]] = {}
        for app in apps.get_app_configs():
            if app.name == "tasks":
                continue  # Ignore this app.
            module_name = f"{app.name}.actions"
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue  # The `actions` module doesn't exist for this app, ignore it
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                # Check if the attribute is a class, a subclass of ActionBase, and not ActionBase itself
                if not (isinstance(attribute, type) and issubclass(attribute, ActionBase) and attribute != ActionBase):
                    continue
                for required in ["name", "progress_title", "progress_subject"]:
                    if not hasattr(attribute, required):
                        raise ValueError(f"Missing required `{required}` variable in `{module_name}.{attribute_name}`")
                self._registered_actions[attribute.name] = attribute
        logger.debug("Registered the following actions: " + ", ".join(self._registered_actions.keys()))

    @cache
    def get_progress_title(self, action: str) -> str:
        action_type: type[ActionBase] = self._registered_actions[action]
        return action_type.get_progress_title()

    @cache
    def get_progress_subject(self, action: str) -> str:
        action_type: type[ActionBase] = self._registered_actions[action]
        return action_type.get_progress_subject()

    @cache
    def get_status_fields(self, action: str) -> list[TaskStatusField]:
        action_type: type[ActionBase] = self._registered_actions[action]
        return action_type.get_status_fields()

    def create_action(self, action: str, task_id: str, log: logging.Logger) -> ActionBase:
        action_type: type[ActionBase] = self._registered_actions[action]
        return action_type(task_id, log)


class LazyActionManager(LazyObject):
    def _setup(self):
        self._wrapped = ActionManager()


action_manager: Union[ActionManager, LazyActionManager] = LazyActionManager()
