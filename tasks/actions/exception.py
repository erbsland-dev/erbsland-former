#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


class ActionError(Exception):
    """
    An exception thrown if the action runs into an unrecoverable problem.
    """

    def __init__(self, message: str, technical_details: str = ""):
        """
        An error within an action.

        :param message: A message that is displayed in the frontend.
        :param technical_details: Technical details that are logged, but not displayed.
        """
        super().__init__(message, technical_details)
        self._message = message
        self._technical_details = technical_details

    @property
    def message(self):
        return self._message

    @property
    def technical_details(self):
        return self._technical_details


class ActionStoppedByUser(Exception):
    """
    An exception thrown if the user stopped the action.
    """

    pass
