#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum


class EgressStep(enum.StrEnum):
    """
    The steps for the egress operation assistant.
    """

    SETUP = "setup"
    """Initial page with checks where the user can choose the export format."""

    RUNNING = "running"
    """The documents are collected and prepared for the chosen export."""

    DONE = "done"
    """The export is done. A download link is displayed for a file export."""
