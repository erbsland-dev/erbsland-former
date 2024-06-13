#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cached_property
from typing import Type, Any

from django.contrib import messages
from django.core.exceptions import BadRequest
from django.utils.translation import gettext_lazy as _

from ai_transformer.tools.model_manager import model_info_manager
from ai_transformer.transformer.user_settings import AiUserSettings
from backend.models import TransformerUserSettings
from backend.transformer.data.regex_definition import RegExDefinition
from backend.transformer.settings_handler import SettingsHandler, SettingsClass
from ai_transformer.transformer.profile_settings import AiProfileSettings, RESULT_ACTION_LABELS, AiProfileResultDetector
from design.views.action import ActionHandlerResponse


class AiProfileSettingsHandler(SettingsHandler[AiProfileSettings]):
    """
    Class to handle the profile settings.
    """

    CHAT_HISTORY_TOKEN_LIMIT_MAX = 100_000_000
    RETRY_COUNT_MAX = 100
    MAX_TOKENS_LIMIT_MAX = 100_000_000
    SESSION_CURRENT_PAGE = "ai_transformer.ai_prompt_page"

    def get_class(self) -> Type[SettingsClass]:
        return AiProfileSettings

    def get_template(self) -> str:
        return "ai_transformer/profile_settings.html"

    def get_default(self) -> SettingsClass:
        return AiProfileSettings()

    def get_post_name_prefix(self) -> str:
        return "ai_"

    def _get_detector_value(self, name: str, index: int, cast_type: Type = str) -> Any:
        return self.get_post_value(f"result_detector.{index + 1}.{name}", cast_type=cast_type)

    def update_settings_from_request(self) -> None:
        page_id = self.get_post_value("current_page", "")
        if page_id not in ["ai_prompt_page", "ai_response_page", "ai_advanced_page"]:
            page_id = ""
        self.request.session[self.SESSION_CURRENT_PAGE] = page_id
        self.settings.model = self.get_post_value("model")
        self.settings.system_prompt = self.get_post_value("system_prompt")
        self.settings.prompt = self.get_post_value("prompt")
        self.settings.fix_surrounding_newlines = self.get_post_value("fix_surrounding_newlines", cast_type=bool)
        self.settings.chat_history = self.get_post_value("chat_history", cast_type=bool)
        self.settings.chat_history_token_limit = self.get_post_value("chat_history_token_limit", 0, cast_type=int)
        self.settings.chat_history_token_limit = min(
            self.settings.chat_history_token_limit, self.CHAT_HISTORY_TOKEN_LIMIT_MAX
        )
        self.settings.extract_result = RegExDefinition(pattern=self.get_post_value("extract_result.pattern"))
        self.settings.extract_result.assign_flags(
            lambda flag: self.get_post_value(f"extract_result.{flag.name}", cast_type=bool)
        )
        for index, detector in enumerate(self.settings.result_detectors):
            detector.pattern = self._get_detector_value("pattern", index)
            detector.assign_flags(lambda flag: self._get_detector_value(flag.name, index, cast_type=bool))
            detector.action = self._get_detector_value("action", index)
            detector.invert = self._get_detector_value("invert", index, cast_type=bool)
        self.settings.retry_count_on_failure = min(
            self.get_post_value("retry_count_on_failure", "0", cast_type=int), self.RETRY_COUNT_MAX
        )
        self.settings.retry_count_on_technical = min(
            self.get_post_value("retry_count_on_technical", "0", cast_type=int), self.RETRY_COUNT_MAX
        )
        self.settings.max_tokens = min(self.get_post_value("max_tokens", "0", cast_type=int), self.MAX_TOKENS_LIMIT_MAX)
        self.settings.force_json_format = self.get_post_value("force_json_format", cast_type=bool)

    def _get_result_detector_index(self) -> int:
        """
        Get the definition index from the action value, or raise an exception if it is out of range.
        """
        try:
            index = int(self.action_value) - 1
            if index < 0 or index >= len(self.settings.result_detectors):
                raise BadRequest("Index out of range.")
            return index
        except ValueError:
            raise BadRequest("Invalid action value")

    def handle_result_detector_delete(self) -> None:
        index = self._get_result_detector_index()
        del self.settings.result_detectors[index]
        messages.info(self.request, _("Deleted the result detector."))

    def handle_result_detector_duplicate(self) -> None:
        index = self._get_result_detector_index()
        definition_copy = self.settings.result_detectors[index].copy()
        self.settings.result_detectors.insert(index + 1, definition_copy)
        messages.info(self.request, _("Duplicated the result detector."))

    def handle_result_detector_move_top(self) -> None:
        index = self._get_result_detector_index()
        self.settings.result_detectors.insert(0, self.settings.result_detectors.pop(index))
        messages.info(self.request, _("Moved the result detector."))

    def handle_result_detector_move_bottom(self) -> None:
        index = self._get_result_detector_index()
        self.settings.result_detectors.append(self.settings.result_detectors.pop(index))
        messages.info(self.request, _("Moved the result detector."))

    def handle_result_detector_move_up(self) -> None:
        index = self._get_result_detector_index()
        if index > 0:
            self.settings.result_detectors[index], self.settings.result_detectors[index - 1] = (
                self.settings.result_detectors[index - 1],
                self.settings.result_detectors[index],
            )
            messages.info(self.request, _("Moved the result detector."))

    def handle_result_detector_move_down(self) -> None:
        index = self._get_result_detector_index()
        if index < len(self.settings.result_detectors) - 1:
            self.settings.result_detectors[index], self.settings.result_detectors[index + 1] = (
                self.settings.result_detectors[index + 1],
                self.settings.result_detectors[index],
            )
            messages.info(self.request, _("Moved the result detector."))

    def handle_result_detector_add(self) -> ActionHandlerResponse:
        self.settings.result_detectors.append(AiProfileResultDetector())
        messages.info(self.request, _("Added a new result detector."))
        return None

    @cached_property
    def has_no_api_key_set(self) -> bool:
        settings_obj = TransformerUserSettings.objects.get_or_create_default(
            self.request.user, transformer_name="gpt_edit"
        )
        settings: AiUserSettings = settings_obj.get_settings()
        return not bool(settings.get_api_key())

    def handle_save_and_close(self) -> ActionHandlerResponse:
        del self.request.session[self.SESSION_CURRENT_PAGE]
        return super().handle_save_and_close()

    def get_context(self) -> dict:
        context = super().get_context()
        current_page = self.request.session.get(self.SESSION_CURRENT_PAGE, "")
        context.update(
            {
                "no_api_key_set": self.has_no_api_key_set,
                "model_list": model_info_manager.get_model_list(),
                "result_action_labels": RESULT_ACTION_LABELS,
                "ai_current_page": current_page,
            }
        )
        return context
