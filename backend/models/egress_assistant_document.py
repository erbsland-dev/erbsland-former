#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.models.egress_assistant import EgressAssistant


class EgressAssistantDocument(models.Model):
    """
    A document that was selected when the egress assistant was started.
    """

    egress_assistant = models.ForeignKey(EgressAssistant, on_delete=models.CASCADE, related_name="documents")
    """The egress assistant that is the owner of this file."""

    order_index = models.IntegerField()
    """A integer that is used to represent the order of the documents as they were selected.
    As the documents are selected at random from a file structure, this field is used to keep
    the original ordering as good as possible."""

    document = models.ForeignKey("Document", on_delete=models.CASCADE, related_name="+")
    """The document."""

    class Meta:
        verbose_name = _("Egress Assistant Document")
        verbose_name_plural = _("Egress Assistant Documents")
        indexes = [
            models.Index(fields=["egress_assistant"], name="eg_assist_doc_main_idx"),
            models.Index(fields=["order_index"], name="eg_assist_doc_order_idx"),
        ]
