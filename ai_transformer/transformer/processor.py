#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import json
import logging
import re
from typing import Any, Optional

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ai_transformer.tools import text_formatter
from ai_transformer.tools.bridge import Bridge
from ai_transformer.tools.chat_history import AiChatHistory
from ai_transformer.tools.chat_messages import AiChatMessages
from ai_transformer.tools.chat_response import AiChatResponse
from ai_transformer.tools.processor_stats import AiProcessorStats
from ai_transformer.tools.model_manager import model_info_manager
from ai_transformer.tools.model_info import ModelInfo
from ai_transformer.transformer.user_settings import AiUserSettings
from backend.enums import TransformerStatus
from backend.syntax_handler import syntax_manager
from backend.transformer.context import TransformerFragmentContext, TransformerDocumentContext
from backend.transformer.error import TransformerError
from backend.transformer.processor import Processor
from backend.transformer.result import ProcessorResult
from ai_transformer.transformer.profile_settings import AiProfileSettings, AiProfileResultAction

logger = logging.getLogger(__name__)


class AiProcessor(Processor[AiProfileSettings, AiUserSettings]):
    """
    The processor to transform document fragments using configured regular expressions.
    """

    RE_PLACEHOLDER = re.compile(r"\{(\w+)(?::(plain|json))?\}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._replacement_values: dict[str, str] = {}  # Keep replacement values active.
        self._maximum_request_size = 0  # The calculated maximum size for requests.
        self.model_info: Optional[ModelInfo] = None  # Info about the used model.
        self.bridge: Optional[Bridge] = None  # The bridge to communicate with the model.
        self.chat_history: Optional[AiChatHistory] = None  # A history of chat messages to fill in.
        self.re_extract_content: Optional[re.Pattern] = None  # The RE to extract the edit from the output.
        self.stats: AiProcessorStats = AiProcessorStats()  # Stats

    def initialize(self):
        if not self.user_settings:
            raise TransformerError(_("No user settings provided."))
        allowed_models = settings.AI_ALLOWED_MODELS
        if allowed_models and self.profile_settings.model not in allowed_models:
            raise TransformerError(
                _("Using model '%(model_name)s' is not allowed on this server.")
                % {"model_name": self.profile_settings.model}
            )
        self.model_info = model_info_manager.get_model(self.profile_settings.model)
        self.chat_history = AiChatHistory(self.model_info)
        self.log_info(
            f"Using model '{self.model_info.identifier}' and context window {self.model_info.context_window}."
        )
        self.bridge = self.model_info.create_bridge()
        self.bridge.set_log_receiver(self)
        self.bridge.set_model_info(self.model_info)
        self.bridge.setup(self.user_settings, self.profile_settings)
        self.bridge.initialize()
        if self.profile_settings.extract_result.pattern:
            self.re_extract_content = self.profile_settings.extract_result.regexp
        self._calculate_maximum_request_size()

    def _calculate_maximum_request_size(self):
        self._maximum_request_size = self.profile_settings.chat_history_token_limit
        if self._maximum_request_size > 0:
            self._maximum_request_size = min(self._maximum_request_size, self.model_info.context_window)
        else:
            self._maximum_request_size = self.model_info.context_window
        self.log_debug(f"Calculated a request token maximum of {self._maximum_request_size} tokens.")

    def replace_placeholders(self, text: str) -> str:
        def replace(match: re.Match) -> str:
            variable_name = match.group(1)
            if variable_name not in self._replacement_values:
                return ""
            value = self._replacement_values[variable_name]
            formatting = match.group(2) or "plain"
            if formatting == "plain":
                return text_formatter.plain(value)
            elif formatting == "json":
                return json.dumps(value)

        return self.RE_PLACEHOLDER.sub(replace, text)

    def document_begin(self, context: TransformerDocumentContext) -> None:
        self._replacement_values.update(context.to_dict())
        self._replacement_values["markdown_block_identifier"] = syntax_manager.get_markdown_block_identifier(
            context.document_syntax
        )

    def fragment_begin(self, context: TransformerFragmentContext) -> None:
        self._replacement_values.update(context.to_dict())

    def transform(self, content: str, context: TransformerFragmentContext) -> ProcessorResult:
        self._replacement_values["content"] = content
        messages = self._prepare_messages(self.profile_settings.prompt)
        response = self.bridge.request_completion(messages)
        self.chat_history.add_response(response)
        self.stats.add_response(response)
        processor_result = self._extract_content(content, response)
        return processor_result

    def _prepare_messages(self, prompt: str) -> AiChatMessages:
        messages = AiChatMessages(self.model_info, self._maximum_request_size)
        system_message = self.replace_placeholders(self.profile_settings.system_prompt)
        messages.set_system_message(system_message)
        user_prompt = self.replace_placeholders(prompt)
        messages.set_user_prompt(user_prompt)
        messages.fill_chat_history(self.chat_history)
        return messages

    def _extract_content(self, original_content: str, response: AiChatResponse) -> ProcessorResult:
        response_output = response.collected_output
        for index, result_detector in enumerate(self.profile_settings.result_detectors):
            if result_detector.detect(response_output):
                action = result_detector.action
                if action == AiProfileResultAction.TRANSFORMATION_FAILED:
                    regex_lines = "\n  ".join(result_detector.to_log_lines())
                    self.log_debug(
                        f"Result detector rule {index + 1} triggered a failure.",
                        f"Regular expression:\n  {regex_lines}\n"
                        f"Prompt:\n{response.collected_input}\nTested Output:\n{response_output}",
                    )
                    return ProcessorResult(
                        content="",
                        output=response_output,
                        status=TransformerStatus.FAILURE,
                        failure_reason=f"Result detector rule {index + 1} triggered the failure.",
                        failure_input=response.collected_input,
                    )
                elif action == AiProfileResultAction.COPY_UNCHANGED:
                    return ProcessorResult(
                        content=original_content, output=response_output, status=TransformerStatus.SUCCESS
                    )
        new_content = response_output
        if self.re_extract_content:
            match = self.re_extract_content.search(new_content)
            if match:
                new_content = match.group(1)
        if self.profile_settings.fix_surrounding_newlines:
            new_content = text_formatter.fix_surrounding_newlines(original_content, new_content)
        return ProcessorResult(content=new_content, output=response_output, status=TransformerStatus.SUCCESS)

    def get_statistics(self) -> dict[str, Any]:
        return self.stats.to_statistic(self.model_info)

    def get_status_values(self) -> dict[str, str]:
        return self.stats.to_status(self.model_info)
