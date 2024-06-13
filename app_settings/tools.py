#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import importlib


def apply_app_default_settings(app_settings_module: str):
    """
    This method sets default settings from the `app_settings_module`.

    :param app_settings_module: The app settings module, like `example.settings`
    """
    from django.conf import settings as django_settings

    local_settings = importlib.import_module(app_settings_module)
    for name in dir(local_settings):
        if name.isupper():
            if not hasattr(django_settings, name):
                setattr(django_settings, name, getattr(local_settings, name))
