#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import base64
import hashlib
from functools import cache

from cryptography.fernet import MultiFernet, Fernet
from django.conf import settings


def _get_keys() -> list[bytes]:
    """
    Get the keys from the settings.

    :return: A list of base64-encoded keys derived from the main and fallback keys.
    :raises ValueError: If the main key is not set or no string, or if the fallbacks are not a list.
    """
    main_key = settings.BACKEND_ENCRYPTION_KEY
    if not main_key or not isinstance(main_key, str):
        raise ValueError("`BACKEND_ENCRYPTION_KEY` not set or no string.")

    result = [base64.urlsafe_b64encode(hashlib.sha256(main_key.encode("utf-8")).digest())]

    if not isinstance(settings.BACKEND_ENCRYPTION_KEY_FALLBACKS, list):
        raise ValueError("`BACKEND_ENCRYPTION_KEY_FALLBACKS` is no list.")

    for fallback_key in settings.BACKEND_ENCRYPTION_KEY_FALLBACKS:
        key_for_result = base64.urlsafe_b64encode(hashlib.sha256(fallback_key.encode("utf-8")).digest())
        if key_for_result in result:
            raise ValueError("Duplicate key in `BACKEND_ENCRYPTION_KEY_FALLBACKS` found.")
        result.append(key_for_result)

    return result


@cache
def _get_fernet() -> MultiFernet:
    """
    Create the Fernet instance for all encrypt/decrypt operations.

    :return: A MultiFernet instance.
    """
    return MultiFernet([Fernet(key) for key in _get_keys()])
