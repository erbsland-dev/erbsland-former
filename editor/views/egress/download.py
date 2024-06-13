#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from datetime import datetime
from pathlib import Path

from django.http import Http404, FileResponse
from django.views import View

from editor.views.egress.access import EgressAccessMixin


class EgressDownloadView(EgressAccessMixin, View):
    """
    A view that allows downloading an exported ZIP file that was prepared by the egress assistant.

    The main reason why this view is to protect the download and only make it accessible to the authenticated
    that runs the assistant.
    """

    def get(self, request, *args, **kwargs):
        if not self.assistant:
            raise Http404()
        path = Path(self.assistant.working_directory) / "export.zip"
        if not path.is_file():
            raise Http404()
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        response = FileResponse(path.open("rb"), as_attachment=True, filename=filename)
        return response
