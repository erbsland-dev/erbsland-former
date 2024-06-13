#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


class TitleMixin:
    """
    This class provides a mixin that allows setting a title and page icon classes for a webpage.
    """

    page_title: str = ""
    """The primary page title."""

    page_title_prefix: str = ""
    """A prefix for the title, that is displayed like '[prefix]: [title]'"""

    page_title_suffix: str = ""
    """A suffix for the title, that is displayed like '[title][suffix]'"""

    page_icon_name: str = ""
    """Optional fontawesome classes to display a page's icon.'"""

    def get_page_title(self) -> str:
        return self.page_title

    def get_page_title_prefix(self) -> str:
        return self.page_title_prefix

    def get_page_title_suffix(self) -> str:
        return self.page_title_suffix

    def get_page_icon_name(self) -> str:
        return self.page_icon_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": self.get_page_title(),
                "page_title_prefix": self.get_page_title_prefix(),
                "page_title_suffix": self.get_page_title_suffix(),
                "page_icon_name": self.get_page_icon_name(),
            }
        )
        return context
