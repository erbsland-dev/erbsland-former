#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

AI_API_KEY = ""
"""
Set the API key globally for all users of this server.
"""

AI_ORGANIZATION_ID = ""
"""
Set the team id globally for all users of this server.
"""

AI_PROJECT_ID = ""
"""
Set the project id globally for all users of this server.
"""

AI_BASE_URL = "https://api.openai.com/v1/"
"""
The base URL for the OpenAI API.
"""

AI_ALLOW_USER_OVERRIDES = True
"""
If set to `True`, each user can set a custom API key and team id, override the values
globally configured for the server.
"""

AI_ALLOWED_MODELS = []
"""
When empty, all implemented language models from the OpenAI interface can be selected.
Otherwise, specify a list of model identifiers (like "gpt-3.5-turbo"), a user can select for their profiles.
"""
