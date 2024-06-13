#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum
import re
from dataclasses import dataclass
from functools import cached_property

from django.utils.translation import gettext_lazy as _

from backend.transformer.data.regex_definition import RegExDefinition
from backend.transformer.settings import TransformerSettingsBase


class AiProfileResultAction(enum.StrEnum):
    TRANSFORMATION_FAILED = "transformation_failed"
    """If the regular expression matches, the transformation has failed."""
    COPY_UNCHANGED = "copy_unchanged"
    """If the regular expression matches, copy the original text with no changes."""


@dataclass
class AiProfileActionLabel:
    action: AiProfileResultAction
    label: str


RESULT_ACTION_LABELS = [
    AiProfileActionLabel(AiProfileResultAction.TRANSFORMATION_FAILED, _("Transformation Failed")),
    AiProfileActionLabel(AiProfileResultAction.COPY_UNCHANGED, _("Copy Unchanged")),
]


class AiProfileResultDetector(RegExDefinition):
    """
    A single trigger to verify results.
    """

    serialized_name = "ai_profile_result_detector"
    serialized_version = 1

    def __init__(
        self,
        pattern: str = "",
        flags: str = "",
        action: str = AiProfileResultAction.TRANSFORMATION_FAILED,
        invert: bool = False,
    ):
        super().__init__(pattern, flags)
        if isinstance(action, AiProfileResultAction):
            action = str(action)
        self.action: str = action  # The action to execute if the regular expression matches.
        self.invert: bool = invert  # If set, the action is executed if the regular expression does NOT match.

    def detect(self, text: str) -> bool:
        result = bool(self.regexp.search(text))
        if self.invert:
            result = not result
        return result


class AiProfileSettings(TransformerSettingsBase):
    """
    The settings for an AI transformer profile.
    """

    serialized_classes = [RegExDefinition, AiProfileResultDetector]

    def __init__(self):
        # Prompt Configuration
        self.model: str = "gpt-4o"
        """The identifier of the language model used for processing."""
        self.system_prompt: str = (
            "You are a helpful assistant translating text from English to German. "
            "The user will give you a fragment of a text, enclosed between the tags [text] and [/text]. "
            "Only translate the text between these two tags from English to German.\n\n"
            "If the user prompt also contains context information, enclosed between the tags [context] and [/context], "
            "use this context to inform your translation.\n\n"
            "Always enclose your translated output between the tags [output] and [/output]. "
            "If you wish to comment on your translation, do so outside of these tags.\n\n"
            "If the input format is incorrect or tags are missing, "
            "respond with an error message specifying the issue.\n\n"
            'In case of an error, always start your output with the text "Error:".'
        )
        """The system prompt that is always sent as first part of every request."""
        self.prompt: str = "[text]\n{content:plain}\n[/text]"
        """The user prompt that is sent as last element in the request."""
        self.chat_history: bool = True
        """If previous requests/response shall be included in each request."""
        self.chat_history_token_limit: int = 50_000
        """A token limit for the prompt and its added chat history."""
        self.dynamically_reduce_token_limit: bool = True
        """Dynamically reduce the token limit when 'context_length_exceeded' errors are returned."""

        # Result Configuration
        self.extract_result = RegExDefinition(pattern=R"\[output\]\n?(.*)\[/output\]", flags="si")
        """Regular expression to extract only a part of the transformed text from the result.
        The first group must contain the result. If it does not match, or if it isn't defined,
        the transformer copies the whole output from the model as result."""
        self.fix_surrounding_newlines: bool = True
        """Fix the surrounding newlines by matching them to the original text."""
        self.max_tokens: int = 0
        """A limit for the maximum number of tokens generated in the response."""
        self.result_detectors: list[AiProfileResultDetector] = [
            AiProfileResultDetector(
                pattern=R"(?i)^\s*\"?Error", flags="si", action=AiProfileResultAction.TRANSFORMATION_FAILED
            ),
            AiProfileResultDetector(
                pattern=R"\[output\].*\[/output\]",
                flags="si",
                action=AiProfileResultAction.TRANSFORMATION_FAILED,
                invert=True,
            ),
        ]
        """Result detectors are tested in the defined order. The action of the first matching one is used.
        If no detector matches, the transformation is considered successful."""

        # Advanced Configuration
        self.retry_count_on_failure: int = 0
        """How many times the same prompt is repeated if the result failed."""
        self.retry_count_on_technical: int = 3
        """How many times to retry on network error, or any other technical error."""
        self.force_json_format: bool = False
        """Force JSON format for the result, see API documentation for details."""
