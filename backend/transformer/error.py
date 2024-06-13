#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


class TransformerError(Exception):
    def __init__(self, message, *, failure_input: str = None, failure_output: str = None):
        super().__init__(message)
        self.failure_input = failure_input
        self.failure_output = failure_output
