#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import abc
import logging

from django.http import HttpRequest


class ApiHandler:
    """
    A handler for the API interface.
    """

    action = ""  # The name of the action in the API

    def __init__(self, request: HttpRequest, logger: logging.Logger):
        self.request = request
        self.logger = logger

    @abc.abstractmethod
    def handle(self, task_id: str, data: dict) -> dict:
        """
        Handle an API request

        :param task_id: The task ID.
        :param data: The data from the request.
        :return: The output.
        """
        pass
