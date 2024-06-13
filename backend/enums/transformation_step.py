#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum


class TransformationStep(enum.StrEnum):
    """
    The steps for the transformer assistant.
    """

    PROFILE = "profile"
    """The user selects a transformation profile."""

    SETUP = "setup"
    """The user sets up the transformer."""

    PREVIEW = "preview"
    """A preview that shows the transformed fragments."""

    TRANSFORMATION_RUNNING = "transformation_running"
    """The project is being transformed."""

    DONE = "done"
    """The transformation is done."""
