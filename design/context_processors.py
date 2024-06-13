#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass, field

CONTEXT_PAGE_END_SCRIPTS = "page_end_scripts"


class PageEndScripts:
    """
    Block of data to handle the page end scripts for the design.
    """

    def __init__(self):
        self._includes: list[str] = []
        self._code: list[str] = []

    @property
    def includes(self) -> list[str]:
        return sorted(self._includes)

    @property
    def code(self) -> str:
        return "\n".join(sorted(self._code))

    def add_include_once(self, url: str) -> None:
        """
        Add a top include URL once.

        :param url: The URL to add.
        """
        if url not in self._includes:
            self._includes.append(url)

    def add_code(self, code: str) -> None:
        """
        Add code to the bottom of the page.

        :param code: The code to be executed.
        """
        self._code.append(code)

    def add_code_once(self, code: str) -> None:
        """
        Add code to the bottom of the page only once.

        :param code: The code statement.
        """
        if code not in self._code:
            self.add_code(code)


def end_page_scripts(request):
    """
    This context processor creates a set for javascript files that shall be included at the end of the page.
    """
    return {CONTEXT_PAGE_END_SCRIPTS: PageEndScripts()}
