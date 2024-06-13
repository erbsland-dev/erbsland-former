#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from backend.enums.ingest_step import IngestStep
from design.views.generic import FormView
from .access import IngestAccessMixin


def get_max_file_size() -> str:
    from django.conf import settings

    return filesizeformat(settings.BACKEND_INGEST_UPLOAD_FILE_SIZE)


def file_size_validator(value):
    from django.conf import settings

    if value.size > settings.BACKEND_INGEST_UPLOAD_FILE_SIZE:
        raise ValidationError(_("The maximum supported file size is %(max_size)s") % {"max_size": get_max_file_size()})


class IngestUploadForm(forms.Form):
    """
    A custom form with just the upload field.
    """

    new_document = forms.FileField(
        label=_("New Document"),
        validators=[file_size_validator],
        help_text=_("The maximum supported file size is %(max_size)s") % {"max_size": get_max_file_size()},
    )


class IngestUpload(IngestAccessMixin, FormView):
    """
    The view to upload a new file for ingestion.
    """

    template_name = "design/assistant/narrow.html"
    form_class = IngestUploadForm
    intro_text = _(
        "Please select a text file in one of the supported formats, or a ZIP file if you like to upload multiple files."
    )

    def get_form_submit_text(self) -> str:
        return _("Upload File")

    def get_form_submit_icon(self) -> str:
        return "upload"

    def is_assistant_required(self):
        return False

    def form_valid(self, form):
        with transaction.atomic():
            if not self.assistant:
                self.create_assistant_instance(uploaded_file=self.request.FILES["new_document"])
            else:
                self.assistant.file = self.request.FILES["new_document"]
                self.assistant.save()
        self.assistant.analyze_upload(
            success_url=self.get_step_url(IngestStep.SETUP),
            failure_url=self.get_stop_url(),
        )
        return super().form_valid(form)
