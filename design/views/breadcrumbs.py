#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

from design.views.title import TitleMixin


@dataclass
class Breadcrumb:
    """
    A breadcrumb to be displayed in the navigation.
    """

    name: str
    url: str


class BreadcrumbMixin(TitleMixin):
    """
    Mixin to add breadcrumb data to the context
    """

    breadcrumbs_title: str = ""
    breadcrumbs: list[Breadcrumb] = []

    def get_breadcrumbs_title(self) -> str:
        if self.breadcrumbs_title:
            return self.breadcrumbs_title
        title = ""
        if self.get_page_title_prefix():
            title += f"{self.get_page_title_prefix()}: "
        title += self.get_page_title()
        if self.get_page_title_suffix():
            title += f" {self.get_page_title_suffix()}"
        return title

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return self.breadcrumbs.copy()  # Make a copy in case the list is modified in a subclass.

    def is_home(self) -> bool:
        """
        For the home view, the text "Home" is displayed on the navigation.
        """
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "breadcrumbs_title": self.get_breadcrumbs_title(),
                "is_home": self.is_home(),
                "breadcrumbs": self.get_breadcrumbs(),
            }
        )
        return context
