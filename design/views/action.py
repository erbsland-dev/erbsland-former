#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
import re
from typing import Union, Optional

from django.http import (
    HttpResponseBadRequest,
    HttpResponse,
    HttpResponseRedirect,
    HttpRequest,
)

from design.views.generic import PageView, DetailView, FormView

logger = logging.getLogger(__name__)


ActionHandlerResponse = Union[None, str, HttpResponse]


class ActionViewMixin:
    """
    A mixin for views that execute actions on displayed content.

    Create forms making POST requests on the same URL, with a field named `action`. To handle an action with
    a given name, simply define a method to handle the action. For the action `example` you write code like this:

    ```
    def handle_example(self) -> ActionHandlerResponse:
        # handle the action.
        return None
    ```

    The attributes `request`, `action_name` and `action_value` are automatically set, so they can be used in
    the action handler methods.

    - If the handler returns `None`, a redirect to the current request path will be made.
    - If it returns a `HttpResponse` object, it will be returned as a result of the `post` method.
    - If it returns a string, it is expected to be a URL and a redirect to this URL is made.

    See the regular expression `RE_VALID_ACTION_NAME` for valid action names.

    If there is no handler for a given action, the problem is logged and the method `handle_unknown_action()` is
    used to handle the request. If there is no field `action` in the post-request, the method `handle_no_action()`
    is used to handle the request.
    """

    RE_VALID_ACTION_NAME = re.compile("^[_a-z0-9]{1,32}$")

    def __init__(self, *args, **kwargs):
        self.request: HttpRequest = None
        self.action_name: str = ""
        self.action_value: str = ""
        super().__init__(*args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        self.action_name = request.POST.get("action", "")
        self.action_value = request.POST.get("action_value", "")
        if not self.action_name:
            return self._convert_response(self.handle_no_action())
        if not self.RE_VALID_ACTION_NAME.fullmatch(self.action_name):
            return HttpResponseBadRequest("Could not handle a malformed request.")
        action_handler_name = f"handle_{self.action_name}"
        if not hasattr(self, action_handler_name):
            return self._convert_response(self.handle_unknown_action())
        action_handler = getattr(self, action_handler_name)
        if not callable(action_handler):
            raise ValueError(f"The attribute {action_handler_name} must be a callable method.")
        return self._convert_response(action_handler())

    def _convert_response(self, response: ActionHandlerResponse) -> HttpResponse:
        if response:
            if isinstance(response, str):
                return HttpResponseRedirect(response)
            return response
        return HttpResponseRedirect(self.request.path)

    def handle_no_action(self) -> ActionHandlerResponse:
        logger.warning("Unexpected request with no given action.")
        return HttpResponseBadRequest("Could not handle a malformed request.")

    def handle_unknown_action(self) -> ActionHandlerResponse:
        logger.warning(f'Unexpected request with an unknown action name "{self.action_name}".')
        return HttpResponseBadRequest("Could not handle a malformed request.")


class ActionPageView(ActionViewMixin, PageView):
    """
    A generic page that supports actions.
    """

    pass


class ActionDetailView(ActionViewMixin, DetailView):
    """
    A generic detail view that supports actions.
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        # Make sure the object is accessible for action handler methods as Django's `DetailView` only sets
        # this attribute on a `get` request.
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class ActionFormView(ActionViewMixin, FormView):
    """
    A generic form view that also supports actions.

    In order to submit the form itself, it must have the field `action` with the value `submit`. This will
    call the method `handle_submit()` you can overwrite and extend as you like.
    """

    def handle_submit(self):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
