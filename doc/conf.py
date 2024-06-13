#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import re
from pathlib import Path

def get_app_version() -> str:
    settings_file = Path(__file__).parent.parent / "ErbslandFormer" / "app_settings.py"
    settings_text = settings_file.read_text()
    if match := re.search("APP_VERSION = \"(.*?)\"", settings_text, re.IGNORECASE):
        return match.group(1)
    return ""

# -- Project information -----------------------------------------------------
project = 'ErbslandFORMER'
copyright = '2023-2024, Erbsland DEV'
author = 'Erbsland DEV'
release = get_app_version()

# -- General configuration ---------------------------------------------------
extensions = ['sphinx_rtd_theme']
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']