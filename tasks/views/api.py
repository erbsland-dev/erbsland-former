#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
from typing import Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest, HttpRequest, Http404
from django.views import View

from tasks.api.base import ApiHandler
from tasks.api.error import ValidationError
from tasks.api.status import StatusHandler
from tasks.api.stop import StopHandler

logger = logging.getLogger(__name__)


class ApiView(LoginRequiredMixin, View):
    """
    The API for JavaScript to provide real-time updates for running background tasks.
    """

    API_LIST = [StatusHandler, StopHandler]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_map: dict[str, type[ApiHandler]] = dict([(api_cls.action, api_cls) for api_cls in self.API_LIST])

    @staticmethod
    def _validate_request(request: HttpRequest) -> dict:
        if not (0 < int(request.META.get("CONTENT_LENGTH", 0)) <= 1024):
            raise ValidationError("Request payload too large or non-existent")

        if not request.content_type.startswith("application/json"):
            raise ValidationError('Expected content type "application/json".')

        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format")

    @staticmethod
    def _validate_data(data: dict) -> Tuple[str, str]:
        if not isinstance(data, dict):
            raise ValidationError("Data is not a dictionary.")

        if "action" not in data or not isinstance(data["action"], str):
            raise ValidationError("Action key missing or not a string.")
        action = data["action"]

        if "task_id" not in data or not isinstance(data["task_id"], str):
            raise ValidationError("Task ID key missing or not an integer.")
        task_id = data["task_id"]

        return action, task_id

    def post(self, request: HttpRequest, *args, **kwargs):
        task_id = None
        action = None
        try:
            input_data = self._validate_request(request)
            action, task_id = self._validate_data(input_data)
            if action not in self.api_map:
                raise ValidationError(f"Unknown action: {action}.")
            api = self.api_map[action](self.request, logger)
            output_data = api.handle(task_id, input_data)
            return JsonResponse(output_data)

        except ValidationError as error:
            logger.warning(f"Invalid task API request. error={error}, action={action}, task_id={task_id}")
            return HttpResponseBadRequest("Invalid request")

        except Exception as error:
            logger.error(f"Unexpected exception: {error}")
            logger.exception(error, stack_info=True)
            return HttpResponseBadRequest("Invalid request")
