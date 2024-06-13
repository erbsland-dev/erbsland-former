#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from app_settings.tools import apply_app_default_settings

# Apply all defaults for settings not defined by the user.
apply_app_default_settings("backend.settings")
