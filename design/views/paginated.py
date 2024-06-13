#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property
from typing import Union

from django.core.paginator import Paginator
from django.db.models import QuerySet

from design.views.action import ActionHandlerResponse


class PaginatedChildrenMixin:
    """
    This mixin supports a list of paginated children that are part of a parent object.

    It requires the `ActionViewMixin` to be included, to handle the `goto_page` action.

    Your HTML template should look like this:

    ```html
    {% for obj in paginator_page.object_list %}
        {# render your objects #}
    {% endfor %}
    {% pagination_bar paginator_page %}
    ```

    Also, you have to overwrite the methods `get_paginator_parent_id()` and `get_paginator_queryset()`.
    The parent id is used to automatically start at page 1 if the parent object changes. By default, no
    id is returned, what keeps the current page indefinitely unless a manual `set_current_page()` call is made.

    You must also set `paginator_session_prefix` or overwrite `get_paginator_session_prefix()` to set a prefix
    for the variables in the session where the current pagination settings are stored. Each view should use
    its own prefix to avoid conflicts.

    The queryset for the children must exist and return a list with all children in a defined order.
    In your HTML template, use `paginator_page.objects` to show only the objects for a given page.
    """

    _MAX_PAGE_COUNT = 10_000  # A reasonable maximum number of pages.
    _SESSION_PAGE = ".paginator.page"
    _SESSION_PARENT_ID = ".paginator.parent_id"
    _SESSION_ITEMS_PER_PAGE = ".paginator.items_per_page"

    paginator_items_per_page_choices = [10, 25, 50, 100, 250, 500, 1000]
    """A list of possible choices for items per page."""

    paginator_items_per_page_default = 10
    """The default number of items per page when none is set."""

    paginator_session_prefix = ""
    """The default prefix for the session variables, controlling the pagination."""

    def get_paginator_session_prefix(self) -> str:
        """
        Get the session prefix for all paginator variables.
        """
        suffix = self.paginator_session_prefix
        if not suffix:
            raise NotImplementedError("Please set `paginator_session_prefix`!")
        return suffix

    def get_paginator_parent_id(self) -> Union[str, int]:
        """
        Get a string or int with a parent if to detect if a new parent object is displayed.

        :return: A string or int that represents the current parent object whose children are being displayed.
        """
        return ""

    def get_paginator_queryset(self) -> QuerySet:
        """
        Return a queryset for all child objects that shall get paginated.

        :return: A queryset with all child objects that shall get paginated.
        """
        raise NotImplementedError("Please implement `get_paginator_queryset`!")

    @property
    def paginator_page(self) -> int:
        value = self.request.session.get(self._paginator_session_var_name(self._SESSION_PAGE), 1)
        if not value or not isinstance(value, int) or not (1 <= value <= self._MAX_PAGE_COUNT):
            return 1
        return value

    @paginator_page.setter
    def paginator_page(self, value: int):
        self.request.session[self._paginator_session_var_name(self._SESSION_PAGE)] = value

    @property
    def paginator_items_per_page(self) -> int:
        value = self.request.session.get(
            self._paginator_session_var_name(self._SESSION_ITEMS_PER_PAGE),
            self.paginator_items_per_page_default,
        )
        if not value or not isinstance(value, int) or not (0 <= value <= self._MAX_PAGE_COUNT):
            return self.paginator_items_per_page_default
        return value

    @paginator_items_per_page.setter
    def paginator_items_per_page(self, value: int):
        self.request.session[self._paginator_session_var_name(self._SESSION_ITEMS_PER_PAGE)] = value

    def _paginator_session_var_name(self, name) -> str:
        return self.get_paginator_session_prefix() + name

    def _has_parent_id_changed(self) -> bool:
        last_parent_id = self.request.session.get(self._paginator_session_var_name(self._SESSION_PARENT_ID), "")
        current_parent_id = self.get_paginator_parent_id()
        self.request.session[self._paginator_session_var_name(self._SESSION_PARENT_ID)] = current_parent_id
        return last_parent_id != current_parent_id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self._has_parent_id_changed():
            self.paginator_page = 1
        page = self.paginator_page
        queryset = self.get_paginator_queryset()
        paginator = Paginator(queryset, self.paginator_items_per_page)
        if not (1 <= page <= paginator.num_pages):
            page = 1
            self.paginator_page = 1
        paginator_page = paginator.get_page(page)
        context.update(
            {
                "paginator": paginator,
                "paginator_page": paginator_page,
            }
        )
        return context

    def handle_goto_page(self) -> ActionHandlerResponse:
        try:
            page = int(self.action_value)
        except ValueError:
            return None
        if not (1 <= page <= self._MAX_PAGE_COUNT):
            return None
        self.paginator_page = page
        return None
