#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django import template
from django.template.context import RenderContext
from django.utils.html import format_html

from design.templatetags.design import page_end_scripts


register = template.Library()


@register.simple_tag(takes_context=True)
def modal_trigger(context: RenderContext, target: str):
    """
    Use this tag to mark a button or any other html element to open a modal dialogue.

    Usage:
    ```
    <a class="button" ... {% design_modal_trigger 'modal_id' %}>
    ```

    The tag ensures that the required javascript is added at the end of the HTML page for modal dialogues.
    It also marks the HTML element with a data attribute `data-modal-trigger='target'` that is used by the
    javascript to find and add the event to it.

    The event handler checks if the element is disabled. In this case the event does not open the dialogue.

    :param context: The context.
    :param target: The identifier of the modal dialogue.
    """
    page_end_scripts(context).add_code_once("Design.activateModalOverlayTriggers();")
    return format_html('data-modal-trigger="{}"', target)


@register.simple_tag(takes_context=True)
def action_button_trigger(
    context: RenderContext, action_name: str, action_value="", restore_scroll_pos=False, form_url=""
):
    """
    Use this tag to mark a button or any other html element to submit the surrounding form with a given action.

    Usage:
    ```
    <a class="button" ... {% action_button_trigger 'edit' 'value' %}>
    ```

    :param context: The context.
    :param action_name: The name of the action, submitted in the field `action`.
    :param action_value: The optional value of the action, submitted in the field `action_value`.
    :param restore_scroll_pos: Set to `True` if the scroll position shall be restored after the action was clicked.
    :param form_url: An alternative URL for the form to be submitted. This will allow you to enclose HTML code
        with a single very plain form tag `<form method="post">`, direction certain actions to alternate URLs.
    """
    page_end_scripts(context).add_code_once("Design.activateActionButtonTriggers();")
    result = format_html(' data-action-trigger="{}" data-action-value="{}" ', action_name, action_value)
    if restore_scroll_pos:
        result += format_html('data-restore-scroll-pos="1" ')
    if form_url:
        result += format_html('data-action-form-url="{}" ', form_url)
    return result


@register.simple_tag(takes_context=True)
def action_select_trigger(context: RenderContext, action_name: str, restore_scroll_pos=False):
    """
    Use this tag to mark a `<select>`-element to trigger an action when it's selection changes.

    Usage:
    ```
    <div class="control is-expanded">
        <div class="select">
            <select {% action_select_trigger 'select_document' %}>
                <option value="...">...</option>
                ...
            </select>
        </div>
    </div>
    ```

    :param context: The context.
    :param action_name: The name of the action, submitted in the field `action`.
    :param restore_scroll_pos: Set to `True` if the scroll position shall be restored after the action was clicked.
    """
    page_end_scripts(context).add_code_once("Design.activateActionButtonTriggers();")
    result = format_html(' data-action-trigger="{}" data-action-event="change" ', action_name)
    if restore_scroll_pos:
        result += format_html('data-restore-scroll-pos="1" ')
    return result


@register.simple_tag(takes_context=True)
def dropdown_trigger(context: RenderContext, menu_id: str):
    """
    Use this tag to mark the dropdown trigger button.

    Usage:
    ```
    <div class="dropdown">
        <div class="dropdown-trigger">
            <button class="button" ... {% dropdown_trigger 'example' %}>
                ...
            </button>
        </div>
        <div class="dropdown-menu" id="example" role="menu">
            ...
        </div>
    </div>
    ```

    :param context: The context.
    :param menu_id: The ID of the menu element.
    """
    page_end_scripts(context).add_code_once("Design.activateDropdownButtonTriggers();")
    return format_html(' aria-haspopup="true" aria-controls="{}" data-dropdown-trigger="1"', menu_id)


@register.simple_tag(takes_context=True)
def tab_trigger(context: RenderContext, page_id: str):
    """
    Use this tag to mark a tab action, in order to dynamically switch tabs.

    Usage:
    ```
    <div class="tabs">
        <ul>
            <li class="is-active"><a {% tab_trigger page_id="page1" %}>{% translate "Page 1" %}</a></li>
            <li><a {% tab_trigger page_id="page2" %}>{% translate "Page 2" %}</a></li>
            <li><a {% tab_trigger page_id="page3" %}>{% translate "Page 3" %}</a></li>
        </ul>
    </div>
    <div class="tabs-content">
        <input type="hidden" name="page_id" value="page1" />
        <div class="tabs-page is-active" id="page1">
            ... Page 1 ...
        </div>
        <div class="tabs-page" id="page2">
            ... Page 2 ...
        </div>
        <div class="tabs-page" id="page3">
            ... Page 3 ...
        </div>
    </div>
    ```
    """
    page_end_scripts(context).add_code_once("Design.activateTabTriggers();")
    return format_html(' data-tab-page="{}"', page_id)
