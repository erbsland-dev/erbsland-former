#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.models import IngestAssistant
from backend.enums import IngestPlanedAction
from backend.tools.definitions import IDENTIFIER_LENGTH, FILENAME_LENGTH, PATH_LENGTH
from backend.tools.validators import (
    filename_validator,
    folder_validator,
    identifier_validator,
    optional_identifier_validator,
)
from backend.storage import working_storage


class IngestDocument(models.Model):
    """
    A single file that will be imported.
    """

    ingest = models.ForeignKey(IngestAssistant, on_delete=models.CASCADE, related_name="documents")
    """The ingest operation that is the owner of this file."""

    local_path = models.CharField(max_length=PATH_LENGTH)
    """The temporary working file path, relative to `working_directory` in the assistant."""

    name = models.CharField(max_length=FILENAME_LENGTH, validators=[filename_validator])
    """The name of the file."""

    folder = models.CharField(max_length=PATH_LENGTH, blank=True, validators=[folder_validator])
    """The folder of the document inside of the project, seperated by `/`."""

    document_syntax = models.CharField(
        blank=True, max_length=IDENTIFIER_LENGTH, validators=[optional_identifier_validator], default=""
    )
    """The syntax that will be used to process this file. `null` if it couldn't get automatically detected."""

    planed_action = models.SmallIntegerField(choices=IngestPlanedAction.choices, default=IngestPlanedAction.IGNORE)
    """The planed action for the import."""

    class Meta:
        verbose_name = _("Ingest Document")
        verbose_name_plural = _("Ingest Documents")
        indexes = [
            models.Index(fields=["ingest", "folder", "name"], name="ingest_document_idx_main"),
            models.Index(fields=["ingest"], name="ingest_document_idx_ingest"),
        ]
