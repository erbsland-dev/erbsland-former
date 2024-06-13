#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import regex

_file_names = R'*?":<>%$&#{}`\|\\'
_private_and_illegal = str(
    R"\uD800-\uDBFF"  # High surrogates
    R"\uDC00-\uDFFF"  # Low surrogates
    R"\uE000-\uF8FF"  # Private use
    R"\uFE00-\uFE0F"  # Variation selectors
    R"\uFFF9-\uFFFF"  # Specials
    R"\U0001FFFE-\U0001FFFF"  # Non characters
    R"\U0002FFFE-\U0002FFFF"  # Non characters
    R"\U0003FFFE-\U0003FFFF"  # Non characters
    R"\U0004FFFE-\U0004FFFF"  # Non characters
    R"\U0005FFFE-\U0005FFFF"  # Non characters
    R"\U0006FFFE-\U0006FFFF"  # Non characters
    R"\U0007FFFE-\U0007FFFF"  # Non characters
    R"\U0008FFFE-\U0008FFFF"  # Non characters
    R"\U0009FFFE-\U0009FFFF"  # Non characters
    R"\U000AFFFE-\U000AFFFF"  # Non characters
    R"\U000BFFFE-\U000BFFFF"  # Non characters
    R"\U000CFFFE-\U000CFFFF"  # Non characters
    R"\U000DFFFE-\U000DFFFF"  # Non characters
    R"\U000E0000-\U000E007F"  # Non characters
    R"\U000E0100-\U000E01EF"  # Variation selectors
    R"\U000EFFFE-\U000EFFFF"  # Non characters
    R"\U000F0000-\U000FFFFF"  # Private use
    R"\U00100000-\U0010FFFD"  # Private use
)
_ctrl_no_lf_tab = (
    str(
        R"\u0000-\u0008\u000b-\u001F\u007F-\u00a0\u00ad"  # ASCII control characters, without linefeed
        R"\u2000-\u200F\u2028-\u202F\u205F-\u206F"  # Special spaces and invisible characters.
    )
    + _private_and_illegal
)
_all_ctrl = (
    str(
        R"\u0000-\u001F\u007F-\u00a0\u00ad"  # ASCII control characters
        R"\u2000-\u200F\u2028-\u202F\u205F-\u206F"  # Special spaces and invisible characters.
    )
    + _private_and_illegal
)

_no_ctrl_no_space = "[^ " + _all_ctrl + "]"
_no_ctrl = "[^" + _all_ctrl + "]"

RE_PROBLEMATIC_FILE_NAME_CHARACTERS = regex.compile(f"[/{_file_names}{_all_ctrl}]")
"""Characters that aren't allowed in filenames."""

RE_PROBLEMATIC_FILE_PATH_CHARACTERS = regex.compile(f"[{_file_names}{_all_ctrl}]")
"""Characters that aren't allowed in paths."""

RE_PROBLEMATIC_TEXT_CHARACTERS = regex.compile(f"[{_all_ctrl}]")
"""Unicode characters that may cause problem when displayed."""

RE_VALID_PLAIN_TEXT = regex.compile(f"(?s)^[^{_ctrl_no_lf_tab}]*$")
"""Valid multi-line plain-text with no special control characters."""

RE_PLAIN_TEXT_INVALID = regex.compile(f"(?s)[{_ctrl_no_lf_tab}]")
"""This matches all invalid characters in supposed plain text to match and remove it."""

RE_VALID_MARKDOWN = regex.compile(f"(?s)^[^{_ctrl_no_lf_tab}]*$")
"""Markdown text with no special control characters."""

RE_VALID_IDENTIFIER = regex.compile("(?s)^[a-zA-Z][_a-zA-Z0-9]{0,31}$")
"""A valid identifier."""

RE_VALID_NAME = regex.compile(f"(?s)^{_no_ctrl_no_space}(?:{_no_ctrl}*{_no_ctrl_no_space})?$")
"""A valid name of an object for display in the UI."""
