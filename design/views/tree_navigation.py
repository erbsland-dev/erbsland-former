#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from typing import Optional


@dataclass
class TreeNavigation:
    has_next: bool  # If clicking next is possible (displays forward).
    has_previous: bool  # If clicking previous is possible (displays backward).
    has_next_sibling: bool = True  # If there is a next sibling object (displays forward one step).
    has_previous_sibling: bool = True  # If there is a previous sibling object (displays backward one step).
    next_title: str = ""  # The title for the next button.
    previous_title: str = ""  # The title for the previous button.
    parent_title: str = ""  # The title for the parent button.


class TreeNavigationMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_tree_navigation(self) -> Optional[TreeNavigation]:
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "tree_nav": self.get_tree_navigation(),
            }
        )
        return context
