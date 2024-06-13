#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import logging

from django import template
from django.conf import settings
from django.core.paginator import Page
from django.template.context import RenderContext

from backend.tools.fraction_bar import FractionBarCounts
from design.context_processors import CONTEXT_PAGE_END_SCRIPTS, PageEndScripts

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag()
def app_version():
    """
    Add the application version.
    """
    return settings.APP_VERSION


@register.inclusion_tag("design/tags/pagination.html", takes_context=True)
def pagination_bar(context: RenderContext, paginator_page: Page, style: str = ""):
    """
    Renders a pagination bar.

    If there are more than 10 pages, automatically use eliding and a [1]...[a][b][c]...[z] style.

    :param context: The context.
    :param paginator_page: The current paginator page.
    :param style: Additional CSS-classes for the style, e.g. 'is-small'.
    """
    paginator = paginator_page.paginator
    page_number = paginator_page.number
    pagination_list: list[dict] = []
    for pagination_page in paginator.get_elided_page_range(page_number):
        if pagination_page != paginator.ELLIPSIS:
            pagination_list.append(
                {
                    "label": f"{pagination_page}",
                    "value": f"{pagination_page}",
                    "is_current": (pagination_page == page_number),
                }
            )
        else:
            pagination_list.append({"label": "", "value": "", "is_current": False})
    if paginator_page.has_previous():
        previous_value = f"{paginator_page.previous_page_number()}"
    else:
        previous_value = ""
    if paginator_page.has_next():
        next_value = f"{paginator_page.next_page_number()}"
    else:
        next_value = ""
    return {
        CONTEXT_PAGE_END_SCRIPTS: context[CONTEXT_PAGE_END_SCRIPTS],  # as we use action buttons.
        "pagination_list": pagination_list,
        "pagination_previous_value": previous_value,
        "pagination_next_value": next_value,
        "pagination_style": style,
    }


@register.inclusion_tag("design/tags/fraction_bar.html")
def fraction_bar(fraction_bar_counts: FractionBarCounts, style: str = ""):
    """
    Renders a fraction bar.

    :param fraction_bar_counts: The data for the fraction bar.
    :param style: Optional additional classes to customize the style.
    """
    return {"fraction_bar_counts": fraction_bar_counts, "style": style}


@register.simple_tag()
def disable_if(condition: bool):
    """
    Simple helper to add the `disable` attribute if the given condition is `true`.

    :param condition: The condition.
    """
    if condition:
        return " disabled "
    return ""


@register.simple_tag()
def disable_if_not(condition: bool):
    """
    Simple helper to add the `disable` attribute if the given condition is `true`.

    :param condition: The condition.
    """
    if not condition:
        return " disabled "
    return ""


@register.simple_tag()
def disable_if_action_flag(action_flags: str, forloop: dict):
    """
    Simple helper to add the `disable` attribute an action has a flag that matches the loop state.

    :param action_flags: The string with action flags.
    """
    if "first" in action_flags and forloop.get("first", False):
        return " disabled "
    if "last" in action_flags and forloop.get("last", False):
        return " disabled "
    return ""


@register.simple_tag()
def checked_if(condition: bool):
    """
    Simple helper to add the `checked` attribute if the given condition is `true`.

    :param condition: The condition.
    """
    if condition:
        return " checked "
    return ""


@register.simple_tag()
def checked_if_not(condition: bool):
    """
    Simple helper to add the `checked` attribute if the given condition is `false`.

    :param condition: The condition.
    """
    if not condition:
        return " checked "
    return ""


@register.simple_tag()
def is_current_if(condition: bool):
    """
    Simple helper for pagination. Adds ` is_current ` class if the condition is `true`.

    :param condition: The condition.
    """
    if condition:
        return " is-current "
    return ""


@register.simple_tag()
def is_active(identifier: str, selected: str, is_default: bool = False):
    """
    Simple helper for displaying tabs/pages. Adds ` is-active ` class if `identifier` and `selected` are equal.

    :param identifier: The identifier for this tab/page.
    :param selected: The identifier from the variable of the selected page.
    :param is_default: Whether the tab/page is default. If `selected` is empty,
        and `is_default` is `True`, tab is selected.
    """
    if identifier == selected or (not selected and is_default):
        return " is-active "
    return ""


@register.simple_tag()
def is_selected(identifier: str, selected: str, is_default: bool = False):
    """
    Simple helper for displaying selection fields. Adds ` selected ` class if `identifier` and `selected` are equal.

    :param identifier: The identifier for this option.
    :param selected: The identifier from the variable of the selected option.
    :param is_default: Whether the option is default. If `selected` is empty,
        and `is_default` is `True`, option is selected.
    """
    if identifier == selected or (not selected and is_default):
        return " selected "
    return ""


def page_end_scripts(context: RenderContext) -> PageEndScripts:
    """
    Access the page end script data.

    :return: The page end script instance.
    """
    if CONTEXT_PAGE_END_SCRIPTS not in context:
        raise ValueError("Please include the context processor `design.context_processors.end_page_scripts`.")
    return context[CONTEXT_PAGE_END_SCRIPTS]


@register.inclusion_tag("design/tags/page_end_scripts.html", takes_context=True)
def include_page_end_scripts(context: RenderContext):
    return {"page_end_scripts": page_end_scripts(context)}


@register.filter()
def with_index(value, arg):
    return f"{value}.{arg}"
