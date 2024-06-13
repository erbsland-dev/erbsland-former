#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from backend.enums.egress_destination import EgressDestination
from backend.tools.regular_expressions import (
    RE_PROBLEMATIC_FILE_NAME_CHARACTERS,
    RE_PROBLEMATIC_FILE_PATH_CHARACTERS,
    RE_VALID_IDENTIFIER,
    RE_VALID_NAME,
    RE_VALID_MARKDOWN,
)


def identifier_validator(value: str):
    """
    A validator for technical internally used identifiers.
    """
    match = RE_VALID_IDENTIFIER.match(value)
    if not match:
        raise ValidationError(_("This text does not match a valid identifier."))


def optional_identifier_validator(value: str):
    """
    A validator for technical internally used identifiers.
    """
    if value:
        match = RE_VALID_IDENTIFIER.match(value)
        if not match:
            raise ValidationError(_("This text does not match a valid identifier."))


def name_validator(value: str):
    """
    A validator for short names that are displayed in the user interface.
    They must not contain any control characters, like line feeds and tabs.
    """
    match = RE_VALID_NAME.match(value)
    if not match:
        raise ValidationError(_("This text does not match a valid name."))


def markdown_validator(value: str):
    """
    A validator for markdown or similar text.
    This text should not contain control characters and illegal unicode characters.
    """
    match = RE_VALID_MARKDOWN.match(value)
    if not match:
        raise ValidationError(_("This text contains illegal control characters."))


def filename_validator(value: str):
    """
    A validator for filenames that work on unix like operating systems.
    """
    if value.startswith(" "):
        raise ValidationError(_("The filename must not start with a space."))
    if value.endswith(" "):
        raise ValidationError(_("The filename must not end with a space."))
    match = RE_PROBLEMATIC_FILE_NAME_CHARACTERS.search(value)
    if match:
        raise ValidationError(
            _("This filename contains an illegal character at position %(pos)d.") % {"pos": match.start()}
        )


def path_validator(value: str):
    """
    A validator for POSIX style paths that work on unix like operating systems.
    """
    if value.startswith((" ", "/")):
        raise ValidationError(_("The folder must not start with a space or slash."))
    if value.endswith((" ", "/")):
        raise ValidationError(_("The folder must not end with a space or slash."))
    match = RE_PROBLEMATIC_FILE_PATH_CHARACTERS.search(value)
    if match:
        raise ValidationError(
            _("This path contains an illegal character at position %(pos)d.") % {"pos": match.start()}
        )


def folder_validator(value: str):
    """
    A validator for POSIX style directory paths that work on unix like operating systems.
    Also limits the directory nesting to maximum eight elements.
    """
    path_validator(value)
    if len(value.split("/")) > 8:
        raise ValidationError(_("This path has more than the allowed eight path elements."))


def egress_destination_validator(value: str):
    try:
        destination = EgressDestination(value)
    except ValueError:
        raise ValidationError(_("This is not a valid egress destination."))
