#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import re

from django.utils.translation import pgettext
from typing import Callable, Optional


RE_SUFFIX_PATTERN = re.compile(
    pgettext(
        "A regular expression pattern, that matches the text from the translation “Suffix for duplicated objects”.",
        r" \(Copy \d+\)$",
    )
)


def get_duplicated_name_suffix(count: int) -> str:
    """
    Get the suffix for a duplicated name.

    :param count: The counter displayed in the suffix.
    :return: The localized suffix.
    """
    return pgettext("Suffix for duplicated db objects.", " (Copy %(count)d)") % {"count": count}


def remove_duplicated_name_suffix(name: str) -> str:
    """
    Remove the suffix for a duplicated name.

    If a name contains a suffix that was created with `get_duplicated_name_suffix`, remove it from the name
    to prevent the suffixes to stack up like `(Copy 1)(Copy 1)`. The difficulty is to handle the
    localized suffixes.

    :param name: The name to remove the suffix from.
    :return: The name without the suffix.
    """
    if match := RE_SUFFIX_PATTERN.search(name):
        return name[: match.start()]
    return name


def get_duplicated_name(
    original_name: str, maximum_length: int, exists_fn: Optional[Callable[[str], bool]] = None
) -> str:
    """
    Get the name of a duplicated item.

    :param original_name: The original name of the object.
    :param maximum_length: The maximum length of the name field.
    :param exists_fn: The function which checks if the name already exists. Takes one string argument and
        returns `True` if the name already exists.
    :return: The new name of the duplicated object.
    """
    original_name = remove_duplicated_name_suffix(original_name)
    count = 1
    while True:
        suffix = get_duplicated_name_suffix(count)
        max_original_length = maximum_length - len(suffix)
        truncated_name = original_name[:max_original_length]
        new_name = f"{truncated_name}{suffix}"
        if not exists_fn or not exists_fn(new_name):
            return new_name
        count += 1
