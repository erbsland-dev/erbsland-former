#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

from backend.enums import TransformerStatus


@dataclass
class ProcessorResult:
    """
    The result of a transformation.
    """

    content: str
    """The new content after the transformation."""

    output: str = ""
    """Output from the transformer (logs, messages, chat)."""

    status: TransformerStatus = TransformerStatus.SUCCESS
    """The status of the transformation."""

    failure_reason: str = ""
    """In case of an failure, the reason why the transformation failed."""

    failure_input: str = ""
    """In case of an failure, the input that caused the transformation to fail."""
