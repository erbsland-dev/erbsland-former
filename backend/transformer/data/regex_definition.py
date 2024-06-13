#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import copy
import re
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Callable

from backend.tools.json_serializable import JsonSerializable


@dataclass
class FlagEntry:
    name: str
    value: bool

    @property
    def title(self) -> str:
        title = self.name[5:].replace("_", " ")
        return title.title()

    @property
    def letter(self) -> str:
        letter = self.name[5:6].upper()
        if letter == "D":
            letter = "S"
        return letter

    @property
    def short_name(self) -> str:
        return self.name.replace("flag_", "")


class RegExDefinition(JsonSerializable):

    serialized_name = "regex_definition"
    serialized_version = 1

    def __init__(self, pattern: str = "", flags: str = ""):
        self.pattern: str = pattern
        self.flag_ascii: bool = "a" in flags
        self.flag_ignore_case: bool = "i" in flags
        self.flag_multiline: bool = "m" in flags
        self.flag_dotall: bool = "s" in flags
        self.flag_verbose: bool = "x" in flags
        self._regex_cache: Optional[re.Pattern] = None

    @cached_property
    def flag_names(self) -> list[str]:
        return ["flag_ignore_case", "flag_multiline", "flag_dotall", "flag_verbose", "flag_ascii"]

    def flags(self) -> list[FlagEntry]:
        """
        Get a list of flag names and their respective values.
        """
        return [FlagEntry(name, getattr(self, name)) for name in self.flag_names]

    @cached_property
    def regexp(self) -> re.Pattern:
        """
        Get the regular that matches this definition.
        """
        if self._regex_cache is None:
            flags = 0
            if self.flag_ascii:
                flags |= re.ASCII
            if self.flag_ignore_case:
                flags |= re.IGNORECASE
            if self.flag_multiline:
                flags |= re.MULTILINE
            if self.flag_dotall:
                flags |= re.DOTALL
            if self.flag_verbose:
                flags |= re.VERBOSE
            self._regex_cache = re.compile(self.pattern, flags)
        return self._regex_cache

    def assign_flags(self, fn: Callable[[FlagEntry], bool]):
        """
        Call the function `fn` for each flag to retrieve its value.

        :param fn: The function that is called with a FlagEntry object and must return a bool.
        """
        for flag in self.flags():
            setattr(self, flag.name, fn(flag))

    def copy(self):
        return copy.deepcopy(self)

    def to_log_lines(self) -> list[str]:
        """
        Create log lines with this regular expression definition for detailed log messages.
        """
        log_lines = []
        log_lines.append(f"Pattern: {self.pattern}")
        flags = [name.replace("flag_", "") for name in self.flag_names if getattr(self, name)]
        log_lines.append("Flags: " + ",".join(flags))
        return log_lines


class RegExReplacement(RegExDefinition):

    serialized_name = "regex_replacement"
    serialized_version = 1

    def __init__(self, pattern: str = "", replacement: str = ""):
        super().__init__(pattern)
        self.replacement: str = replacement

    def transform(self, text: str) -> str:
        """
        Transform the given text using this regex definition.

        :param text: The text to transform.
        :return: The transformed text.
        """
        return self.regexp.sub(self.replacement, text)
