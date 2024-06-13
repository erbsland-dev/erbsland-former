#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.conf import settings
from django.core.checks import register, Tags, Error, Warning


@register(Tags.security)
def check_backend_encryption_key(app_configs, **kwargs):
    errors = []
    if not settings.BACKEND_ENCRYPTION_KEY:
        errors.append(
            Error(
                "The `BACKEND_ENCRYPTION_KEY` settings is not set.",
                hint="Generate a secret key for the `BACKEND_ENCRYPTION_KEY` variable in your copy of `settings.py`",
                id="backend.E001",
            )
        )
    elif not isinstance(settings.BACKEND_ENCRYPTION_KEY, str):
        errors.append(
            Error(
                "The `BACKEND_ENCRYPTION_KEY` setting must be a string.",
                id="backend.E003",
            )
        )
    elif len(settings.BACKEND_ENCRYPTION_KEY) < 32:
        errors.append(
            Error(
                "The `BACKEND_ENCRYPTION_KEY` setting must be at least 32 characters long",
                id="backend.E004",
            )
        )
    elif "-insecure-" in settings.BACKEND_ENCRYPTION_KEY:
        errors.append(
            Warning(
                "Copied unsafe `BACKEND_ENCRYPTION_KEY` default settings.",
                hint="Generate a secret key for the `BACKEND_ENCRYPTION_KEY` variable in your copy of `settings.py`",
                id="backend.E002",
            )
        )
    if not isinstance(settings.BACKEND_ENCRYPTION_KEY_FALLBACKS, list):
        errors.append(
            Error(
                "The `BACKEND_ENCRYPTION_KEY_FALLBACKS` setting must be a list.",
                id="backend.E005",
            )
        )
    elif len(settings.BACKEND_ENCRYPTION_KEY_FALLBACKS) > 3:
        errors.append(
            Error(
                "The `BACKEND_ENCRYPTION_KEY_FALLBACKS` setting is just for a temporary migration. "
                "Make sure to remove old keys as soon all users migrated their settings. Each additional "
                "key impacts the performance of the application.",
                hint="Remove old keys after migration.",
                id="backend.E006",
            )
        )
    return errors
