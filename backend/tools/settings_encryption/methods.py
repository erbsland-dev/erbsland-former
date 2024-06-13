#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import logging

from cryptography.fernet import InvalidToken

from backend.tools.settings_encryption.keys import _get_fernet


def settings_encrypt(text: str) -> str:
    """
    Encrypt settings using the key stored in `BACKEND_ENCRYPTION_KEY`.

    :param text: The text to be encrypted.
    :return: The encrypted text to be stored in the database.
    """
    if not isinstance(text, str):
        raise TypeError("`text` must be a string.")
    if not text:
        return ""
    cipher_suite = _get_fernet()
    encrypted_text = cipher_suite.encrypt(text.encode("utf-8"))
    return encrypted_text.decode("utf-8")


def settings_decrypt(text: str) -> str:
    """
    Decrypt settings using the keys stored in `BACKEND_ENCRYPTION_KEY` and `BACKEND_ENCRYPTION_KEY_FALLBACKS`.

    As this method is used in context of user settings, if the decryption fails, an empty string is returned.
    It is assumed, the application will handle empty passwords or API keys as not defined and will request
    that the user will set them again.

    :param text: The encrypted text from `settings_encrypt`.
    :return: The decrypted text.
    """
    if not isinstance(text, str):
        raise TypeError("`text` must be a string.")
    if not text:
        return ""
    cipher_suite = _get_fernet()
    try:
        decrypted_text = cipher_suite.decrypt(text.encode("utf-8"))
    except InvalidToken as error:
        logging.warning(f"Failed to decrypt setting value. Error: {error}")
        return ""
    return decrypted_text.decode("utf-8")
