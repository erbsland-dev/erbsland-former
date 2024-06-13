#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Tuple

_base_dir = Path(__file__).resolve().parent.parent


BACKEND_ENCRYPTION_KEY = ""
"""
The encryption key that is used to synchronously encrypt/decrypt sensitive user settings.
"""

BACKEND_ENCRYPTION_KEY_FALLBACKS = []
"""
A list of fallback keys to rotate the encryption key.

User settings using fallback keys will not be automatically migrated to the latest key without
user interaction. If you rotate the key, make sure to give users enough time to update passwords and
API keys in the settings before you remove the key from the fallback key list.
"""

BACKEND_IGNORE_SYNTAX_HANDLER: list[str] = []
"""
A list of syntax handler identifiers that shall be ignored.
"""

BACKEND_DEFAULT_SYNTAX_HANDLER: str = "markdown"
"""The default syntax handler to use."""

BACKEND_IGNORE_SIZE_CALCULATOR: list[str] = []
"""
A list with size calculators identifiers that shall be ignored.
"""

BACKEND_TRANSFORMER: list[str] = [
    "regex_transformer.transformers.RegexTransformer",
    "openai_transformer.transformers.OpenAiTransformer",
]
"""
A list with all active transformer classes.
Extend this list with your custom transformers, or remove the ones you don't need.
"""

BACKEND_DEFAULT_SIZE_CALCULATOR: str = "char"
"""The default size calculator"""

BACKEND_INGEST_UPLOAD_FILE_SIZE = 10_000_000
"""The maximum size of uploaded data in bytes."""

BACKEND_INGEST_DOCUMENT_SIZE = 10_000_000
"""The maximum size of a single document (uploaded or extracted)"""

BACKEND_INGEST_FILE_COUNT = 100
"""The maximum number of files imported with one upload."""

BACKEND_WORKING_DIR = _base_dir / "working_dir"
"""The working dir where temporary files are created that are imported/exported into and from the database.
This directory requires read and write access from both the frontend and backend process.
Also, this directory must not be publicly accessible via the webserver (this is no `MEDIA` directory!)"""

BACKEND_SIZE_CALCULATION_MAX_BLOCK_SIZE = 200_000
"""The maximum size of a block of data held in memory to do a size calculation. Individual size calculation
modules can lower this value further but can not increase the limit."""

# --- Options for development ----------------------------------------------------------------------------------------

BACKEND_TEST_ADMIN_NAME: str = "admin"
"""The name of the test admin user for the `reset_test_db` command."""

BACKEND_TEST_ADMIN_PW: str = "test"
"""The password of the test admin user for the `reset_test_db` command."""

BACKEND_TEST_USERS: list[Tuple[str, str, str]] = [
    ("user1", "braved-lends@example.com", "test"),
    ("user2", "darned-vlebs@example.com", "test"),
    ("user3", "lard-sned-bev@example.com", "test"),
]
"""A list of test users for the `reset_test_db` command. username, email, password."""

BACKEND_TEST_PROJECTS: list[dict] = [
    {
        "owner": "user1",
        "name": "Example 1",
        "description": "An example project",
    },
    {
        "owner": "user1",
        "name": "Example 2",
        "description": "An example project",
    },
    {
        "owner": "user2",
        "name": "Example 3",
        "description": "An example project",
    },
]
"""A list of projects to be created with the `reset_test_db` command."""
