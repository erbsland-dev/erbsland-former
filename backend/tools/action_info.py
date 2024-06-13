#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass


@dataclass(frozen=True)
class ActionInfo:
    """
    A generic class to hold information about an action button/tab/link.
    """

    action_name: str
    """The name of the action."""

    title: str = ""
    """The title of the action displayed in the UI."""

    icon_name: str = ""
    """The icon name displayed for the action."""

    color_classes: str = ""
    """Optional color classes to style the action element."""

    disabled_if: str = ""
    """A whitespace separated list of flags when the action is disabled."""
