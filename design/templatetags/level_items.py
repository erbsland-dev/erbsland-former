#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Optional

from django import template
from django.template.context import RenderContext

from design.context_processors import CONTEXT_PAGE_END_SCRIPTS

register = template.Library()


@register.inclusion_tag("design/level_items/action_button.html", takes_context=True)
def action_button(
    context: RenderContext,
    text: str,
    action_trigger: str = "",
    action_value: str = "",
    modal_trigger: str = "",
    url: str = "",
    is_main: Optional[bool] = None,
    button_classes: str = "is-success",
    icon: str = "",
    icon_classes: str = "",
    is_disabled: bool = False,
):
    """
    A level item action button.

    For the button icon, you can either use `icon` or `icon_classes`, but not both. The `icon` parameter specifies
    the name of the icon, which is used to build the FontAwesome classes from it. Using `icon_classes` you can
    specify the classes manually.

    The button style can be either defined using the `button_classes` or using `is_main`. While the first defines
    the classes manually, `is_main` sets the classes to `is-outline is-white` if `False`, or keeps the original
    `button_classes` value unchanged if `True`, which is the default behaviour for the main action in the header.

    :param text: The text on the button.
    :param action_trigger: The name of an action. Adds an action trigger.
    :param action_value: The optional value of the action.
    :param modal_trigger: The name of a modal. Adds a modal trigger.
    :param url: A URL to link to.
    :param is_main: If this is the main action.
    :param button_classes: Classes to style the button.
    :param icon: The name of a font awesome icon.
    :param icon_classes: Classes to display an icon in front of the button text.
    :param is_disabled: If the button is disabled.
    """
    if icon:
        icon_classes = f"fas fa-{icon}"
    if is_main is not None:
        if not is_main:
            button_classes = "is-primary"
    return {
        CONTEXT_PAGE_END_SCRIPTS: context[CONTEXT_PAGE_END_SCRIPTS],
        "text": text,
        "action_trigger": action_trigger,
        "action_value": action_value,
        "modal_trigger": modal_trigger,
        "url": url,
        "button_classes": button_classes,
        "icon_classes": icon_classes,
        "is_disabled": is_disabled,
    }
