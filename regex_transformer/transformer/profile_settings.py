#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from backend.transformer.settings import TransformerSettingsBase
from backend.transformer.data.regex_definition import RegExReplacement


class RegExProfileSettings(TransformerSettingsBase):
    serialized_classes = [RegExReplacement]

    def __init__(self):
        self.definitions: list[RegExReplacement] = [self.default_definition()]

    @staticmethod
    def default_definition() -> RegExReplacement:
        return RegExReplacement(pattern="example", replacement="replacement")

    def add_definition(self, definition: RegExReplacement = None):
        if definition is None:
            definition = self.default_definition()
        elif not isinstance(definition, RegExReplacement):
            raise TypeError("definition must be a RegExReplacement")
        self.definitions.append(definition)
