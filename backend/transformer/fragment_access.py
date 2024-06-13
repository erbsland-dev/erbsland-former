#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from typing import Protocol


class FragmentAccess(Protocol):
    """
    The text that is accessible from a transformer context.
    """

    @property
    def source_text(self) -> str:
        """The source text."""
        ...

    @property
    def has_edit(self) -> bool:
        """`True` if a manual edit exists."""
        ...

    @property
    def edit_text(self) -> str:
        """The edit text, or empty if there is no edit."""
        ...

    @property
    def has_transformation(self) -> bool:
        """`True` if this fragment was transformed."""
        ...

    @property
    def has_failed_transformation(self) -> bool:
        """`True` if the transformer produced an error."""
        ...

    @property
    def transformation_text(self) -> str:
        """The transformed text. Empty if no transformation was done."""
        ...

    @property
    def transformation_output(self) -> str:
        """The transformer output."""
        ...

    @property
    def final_text(self) -> str:
        """The final content. Either the source, transformation or a manual edit."""
        ...
