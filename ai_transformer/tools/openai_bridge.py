#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import json
from typing import Optional

import openai

from django.utils.translation import gettext_lazy as _
from ai_transformer.tools.bridge import Bridge
from ai_transformer.tools.chat_messages import AiChatMessages
from ai_transformer.tools.chat_response import AiChatResponse
from ai_transformer.transformer.profile_settings import AiProfileSettings
from ai_transformer.transformer.user_settings import AiUserSettings
from backend.transformer.error import TransformerError
from tasks.tools.log_level import LogLevel


class OpenAIBridge(Bridge):

    CONTINUE_REQUEST_PROMPT = "continue"
    MAXIMUM_CONTINUE_REQUESTS = 5

    def __init__(self):
        super().__init__()
        self._client: Optional[openai.OpenAI] = None
        self._force_json_format: bool = False

    def setup(self, user_settings: AiUserSettings, profile_settings: AiProfileSettings) -> None:
        api_key = user_settings.get_api_key()
        organization_id = user_settings.get_organization_id()
        project_id = user_settings.get_project_id()
        self._force_json_format = profile_settings.force_json_format
        if not api_key:
            raise TransformerError(_("There is no API key provided."))
        self._client = openai.OpenAI(api_key=api_key, organization=organization_id, project=project_id)

    def initialize(self) -> None:
        try:
            self.log_info("Verifying the provided API key.")
            response = self._client.models.list()
            if not response.data:
                raise TransformerError(_("No models available or invalid response."))
            # Check if the specified model is in the list of available models
            available_models = [model.id for model in response.data]
            self.log_debug("Received a list of available models for that key.", ", ".join(available_models))
            if self.model.identifier not in available_models:
                raise TransformerError(
                    _("The model %(model_name)s is not accessible with the provided API key.")
                    % {"model_name": self.model.identifier}
                )
        except openai.AuthenticationError:
            raise TransformerError(_("Invalid API key or unauthorized access."))
        except openai.OpenAIError as e:
            raise TransformerError(_("OpenAI API error: %(error_message)s") % {"error_message": str(e)})

    def request_completion(self, messages: AiChatMessages) -> AiChatResponse:
        response = AiChatResponse(self.model)
        try:
            self._retrieve_complete_response(messages, response)
            return response
        except openai.OpenAIError as e:
            raise TransformerError(
                _(
                    "OpenAI API error: %(error_message)s\n"
                    "Calculated request size: %(request_size)d Tokens\n"
                    "Model maximum input: %(model_maximum_input)d Tokens\n"
                    "Profile maximum input: %(profile_maximum_input)d Tokens"
                )
                % {
                    "error_message": str(e),
                    "request_size": messages.token_count,
                    "model_maximum_input": self.model.context_window,
                    "profile_maximum_input": messages.maximum_request_size,
                },
                failure_input=response.collected_input,
                failure_output=response.collected_output,
            )

    def _retrieve_complete_response(self, messages: AiChatMessages, chat_response: AiChatResponse) -> AiChatResponse:
        chat_response.add_user_message(messages.user_prompt)
        for continue_try in range(self.MAXIMUM_CONTINUE_REQUESTS):
            request_json = self._prepare_request_json(messages)
            self.log_debug("Sending completion request", json.dumps(request_json, indent=4))
            client_response = self._client.chat.completions.create(**request_json)
            self.log_debug("Received a response.", client_response.to_json(indent=4))
            self._handle_token_counts(messages, client_response, chat_response)
            success = self._handle_model_response(client_response, chat_response)
            if success:  # We got a complete request, return it.
                return chat_response
            # The model stopped somewhere in the middle, encourage it to continue.
            continue_request = self.CONTINUE_REQUEST_PROMPT
            chat_response.add_user_message(continue_request)
            messages = messages.create_followup(client_response.choices[0].message.content, continue_request)
        # At this point, we exceeded the number of continue requests.
        self.log_debug("Incomplete output. Asking the model to continue.")
        raise TransformerError(
            _(
                "Stopped the output from the model after %(count)d continuation prompts. "
                "See output for the received text until this point."
            )
            % {"count": self.MAXIMUM_CONTINUE_REQUESTS},
            failure_input=chat_response.collected_input,
            failure_output=chat_response.collected_output,
        )

    def _prepare_request_json(self, messages: AiChatMessages):
        response_args = {
            "model": self.model.identifier,
            "messages": messages.to_json(),
        }
        if self._force_json_format:
            response_args["response_format"] = {"type": "json_object"}
        return response_args

    def _handle_token_counts(
        self, messages: AiChatMessages, client_response: openai.ChatCompletion, chat_response: AiChatResponse
    ):
        prompt_tokens = client_response.usage.prompt_tokens
        chat_response.add_token_counts(
            input_tokens=prompt_tokens,
            output_tokens=client_response.usage.completion_tokens,
            total_tokens=client_response.usage.total_tokens,
        )
        messages_token_count = messages.token_count
        if messages_token_count != prompt_tokens:
            level = LogLevel.DEBUG
            if abs(messages_token_count - prompt_tokens) > 20:
                level = LogLevel.WARNING
            self.log_message(
                level,
                f"The calculated token count for request ({messages_token_count} tokens) "
                f"does not match the token count returned by the API ({prompt_tokens} tokens)",
            )

    def _handle_model_response(self, client_response: openai.ChatCompletion, chat_response: AiChatResponse) -> bool:
        """
        Handle the model response.

        :param client_response: The raw response from the client.
        :param chat_response: The response object.
        :return: `True` on success, `False` if continue shall be requested.
        """
        choice = client_response.choices[0]
        model_response = choice.message.content
        chat_response.add_assistant_message(model_response)
        match choice.finish_reason:
            case "stop":
                return True
            case "length":
                return False
            case "content_filter":
                raise TransformerError(
                    _("The output was omitted, because it was flagged by a content filter."),
                    failure_input=chat_response.collected_input,
                    failure_output=chat_response.collected_output,
                )
            case "function_call":
                raise TransformerError(
                    _(
                        "The language model suggested to call a function. "
                        "A response to this behaviour is not implemented in this application."
                    ),
                    failure_input=chat_response.collected_input,
                    failure_output=chat_response.collected_output,
                )
            case _:
                self.log_error(f"Received unknown finish reason: {choice.finish_reason}")
                raise TransformerError(
                    _("An unknown finish reason was received from the API."),
                    failure_input=chat_response.collected_input,
                    failure_output=chat_response.collected_output,
                )
