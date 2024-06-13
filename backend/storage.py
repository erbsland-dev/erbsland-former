#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.core.files.storage import FileSystemStorage

from django.conf import settings

working_storage = FileSystemStorage(location=settings.BACKEND_WORKING_DIR)
"""The storage for the working directory that is used while importing and exporting files."""
