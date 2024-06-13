#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum


class IngestStep(enum.StrEnum):
    """
    The steps for the ingest operation assistant.
    """

    UPLOAD = "upload"
    """The upload has not started, the user selects a file."""

    ANALYSIS_RUNNING = "analysis_running"
    """Check the uploaded file(s)."""

    SETUP = "setup"
    """User configures splitting algorithm and document type."""

    PREPARING_PREVIEW = "preparing_preview"
    """The file(s) are split and imported into the database for a preview"""

    PREVIEW = "preview"
    """Preview the data."""

    IMPORTING_DOCUMENTS = "importing_documents"
    """The prepared documents are being imported."""

    DONE = "done"
    """The import is done."""
