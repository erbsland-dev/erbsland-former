#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import time

from backend.enums import TransformerStatus
from backend.transformer.context import TransformerFragmentContext
from backend.transformer.processor import Processor
from backend.transformer.result import ProcessorResult
from regex_transformer.transformer.profile_settings import RegExProfileSettings


class RegExProcessor(Processor[RegExProfileSettings, None]):
    """
    The processor to transform document fragments using configured regular expressions.
    """

    def transform(self, content: str, context: TransformerFragmentContext) -> ProcessorResult:
        for definition in self.profile_settings.definitions:
            content = definition.transform(content)
        return ProcessorResult(content=content, status=TransformerStatus.SUCCESS)
