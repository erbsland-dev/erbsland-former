#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from backend.tools.definitions import IDENTIFIER_LENGTH
from backend.tools.validators import identifier_validator
from backend.transformer import TransformerBase
from backend.transformer.settings import TransformerSettingsBase


class TransformerUserSettingsManager(models.Manager):

    @transaction.atomic
    def get_or_create_default(self, user: User, transformer_name: str) -> "TransformerUserSettings":
        """
        Get or create the default settings for a transformer.

        :param transformer_name: The name of the transformer.
        :return: The settings object.
        """
        try:
            return self.get(transformer_name=transformer_name)
        except ObjectDoesNotExist:
            from backend.transformer.manager import transformer_manager

            transformer: TransformerBase = transformer_manager.get_extension(transformer_name)
            configuration = None
            if transformer.user_settings_handler:
                configuration = transformer.user_settings_handler.get_default().to_json()
            obj = self.create(
                transformer_name=transformer.get_name(),
                settings=user.settings,
                version=transformer.get_version(),
                configuration=configuration,
            )
        return obj


class TransformerUserSettings(models.Model):
    """
    The user settings for a transformer.
    """

    transformer_name = models.CharField(max_length=IDENTIFIER_LENGTH, validators=[identifier_validator])
    """The identifier of the transformer."""

    settings = models.ForeignKey("UserSettings", on_delete=models.CASCADE, related_name="transformer_settings")
    """The user settings object where this transformer settings entry belongs to."""

    version = models.IntegerField()
    """The version of the transformer that created this settings object."""

    configuration = models.JSONField()
    """The JSON data with the user settings for the transformer."""

    objects = TransformerUserSettingsManager()

    @cached_property
    def transformer(self) -> TransformerBase:
        """
        Get the transformer for this profile.

        :return: The transformer instance for this profile.
        """
        from backend.transformer.manager import transformer_manager

        return transformer_manager.get_transformer(self.transformer_name)

    def get_settings(self) -> TransformerSettingsBase:
        """Convert the stored JSON data into a transformer settings object."""
        return self.transformer.user_settings_handler.get_settings_from_json(self.configuration, self.version)

    def update_settings(self, new_settings: TransformerSettingsBase) -> None:
        """
        Update the settings in this object and save it.

        :param new_settings: The new settings to save.
        """
        new_json = new_settings.to_json()
        if self.configuration != new_json:
            self.version = self.transformer.get_version()
            self.configuration = new_settings.to_json()
            self.save()

    class Meta:
        verbose_name = _("TransformerProfile Settings")
        indexes = [
            models.Index(fields=["transformer_name"], name="ts_transformer_name_idx"),
            models.Index(fields=["settings"], name="ts_settings_idx"),
        ]
