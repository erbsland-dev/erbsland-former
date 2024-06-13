#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum


class ContextSource(enum.StrEnum):
    SECTION = "section"  # A section in a document or book. The value is the plain-text of the title of the section.
    BLOCK = "block"  # A statement that groups further lines of text/code. Value is the simplified statement.
