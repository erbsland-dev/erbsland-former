#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import AppConfig


class BackendConfig(AppConfig):
    """
    The configuration of the backend system.
    """

    name = "backend"
    verbose_name = "Backend"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from backend.signals import register_signals
        import backend.checks

        register_signals()
