#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property
from typing import Self

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext

from backend.tools.definitions import IDENTIFIER_LENGTH, NAME_LENGTH
from backend.tools.object_names import get_duplicated_name
from backend.tools.validators import identifier_validator, name_validator, markdown_validator
from backend.transformer import TransformerBase
from backend.transformer.settings import TransformerSettingsBase


class TransformerProfile(models.Model):
    """
    A configured transformation that can be applied to a project or document.
    """

    profile_name = models.CharField(verbose_name=_("Name"), max_length=NAME_LENGTH, validators=[name_validator])
    """The name of the profile, set by the user."""

    transformer_name = models.CharField(
        verbose_name=_("Transformer"), max_length=IDENTIFIER_LENGTH, validators=[identifier_validator]
    )
    """The name of the transformer."""

    description = models.TextField(verbose_name=_("Notes"), blank=True, validators=[markdown_validator])
    """The optional fields for notes about the profile in Markdown format."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transformer_profiles")
    """The owner of this profile."""

    version = models.IntegerField()
    """The version of the transformer for which this settings were created."""

    configuration = models.JSONField()
    """The configuration for the transformer profile."""

    created = models.DateTimeField(auto_now_add=True)
    """The date when the profile was created."""

    modified = models.DateTimeField(auto_now=True)
    """The date when the profile was last modified."""

    def can_user_edit(self, user: User) -> bool:
        """
        Test if the given user can edit this project.

        :param user: The user to test.
        :return: `True` if the given user can edit this project.
        """
        return self.owner == user

    @cached_property
    def transformer(self) -> TransformerBase:
        """
        Get the transformer for this profile.

        :return: The transformer instance for this profile.
        """
        from backend.transformer.manager import transformer_manager

        return transformer_manager.get_transformer(self.transformer_name)

    def get_transformer_verbose_name(self):
        """Get the verbose name of the transformer."""
        return self.transformer.get_verbose_name()

    def get_settings(self) -> TransformerSettingsBase:
        """Convert the stored JSON data into a transformer settings object."""
        return self.transformer.profile_settings_handler.get_settings_from_json(self.configuration, self.version)

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

    def duplicate(self) -> Self:
        """
        Duplicate this profile.
        """

        def does_name_exist(name: str) -> bool:
            return self.__class__.objects.filter(profile_name=name).exists()

        return self.__class__.objects.create(
            profile_name=get_duplicated_name(self.profile_name, NAME_LENGTH, does_name_exist),
            transformer_name=self.transformer_name,
            description=self.description,
            owner=self.owner,
            version=self.version,
            configuration=self.configuration,
        )

    def __str__(self) -> str:
        name = self.profile_name[0:40]
        if len(self.profile_name) > 40:
            name += "…"
        return name

    class Meta:
        verbose_name = _("Transformer Profile")
        verbose_name_plural = _("Transformer Profiles")
        indexes = [
            models.Index(fields=["owner"], name="tf_owner_idx"),
            models.Index(fields=["profile_name"], name="tf_profile_name_idx"),
            models.Index(fields=["modified"], name="tf_modified_idx"),
        ]
