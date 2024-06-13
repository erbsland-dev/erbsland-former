#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import re
from typing import Any


RE_SURROUNDING_NEWLINES = re.compile(r"^([ \t\n]*)(.*?)([ \n\t]*)$", re.DOTALL)


def plain(value: Any) -> str:
    if isinstance(value, str):
        return value
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, list):
        return " ".join(plain(v) for v in value)
    raise NotImplementedError(type(value))


def fix_surrounding_newlines(original_content: str, new_content: str) -> str:
    match = RE_SURROUNDING_NEWLINES.search(original_content)
    prefix = ""
    suffix = ""
    if match:
        prefix = match.group(1)
        suffix = match.group(3)
    match = RE_SURROUNDING_NEWLINES.search(new_content)
    if match:
        new_content = match.group(2)
    return f"{prefix}{new_content}{suffix}"
