#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from typing import Optional, Any

from backend.splitter.text_fragment_node import TextFragmentNode


@dataclass
class SplitterBlock:
    """
    A block created by the splitter.
    """

    text: str = ""
    """The text of the block."""

    size: int = 0
    """The size of the block in the chosen units."""

    line_number: Optional[int] = None
    """The first line number."""

    context: dict[str, Any] = field(default_factory=dict)
    """The dictionary with the collected context data for this block."""
