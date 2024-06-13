#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.models.transformation_assistant import TransformationAssistant


class TransformationAssistantDocument(models.Model):
    """
    A document that was selected when the transformation assistant was started.
    """

    transformation_assistant = models.ForeignKey(
        TransformationAssistant, on_delete=models.CASCADE, related_name="documents"
    )
    """The ingest operation that is the owner of this file."""

    order_index = models.IntegerField()
    """A integer that is used to represent the order of the documents as they were selected.
    As the documents are selected at random from a file structure, this field is used to keep
    the original ordering as good as possible."""

    document = models.ForeignKey("Document", on_delete=models.CASCADE, related_name="+")
    """The document."""

    class Meta:
        verbose_name = _("Transformation Assistant Document")
        verbose_name_plural = _("Transformation Assistant Documents")
        indexes = [
            models.Index(fields=["transformation_assistant"], name="tr_assist_doc_main_idx"),
            models.Index(fields=["order_index"], name="tr_assist_doc_order_idx"),
        ]
