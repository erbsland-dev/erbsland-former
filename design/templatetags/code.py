#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import base64

from django import template
from django.template.context import RenderContext
from django.template.loader import render_to_string
from django.templatetags.static import static

from design.templatetags.design import page_end_scripts
from design.views.diff import UnifiedDiff, SplitDiff, DiffResult

register = template.Library()


@register.inclusion_tag("design/tags/code_block.html")
def code_block(text: str, start_line=1, style=""):
    """
    Render a code block with lines numbers.
    """
    lines = [(index + start_line, line) for index, line in enumerate(text.splitlines(keepends=False))]
    return {
        "lines": lines,
        "start_line": start_line,
        "style": style,
    }


@register.inclusion_tag("design/tags/code_diff_unified.html")
def code_diff_unified(diff: UnifiedDiff, style=""):
    """
    Render a block with a unified diff.

    :param diff: The unified diff from the `views.diff.unified_diff` function.
    :param style: Additional classes to add to the diff block.
    """
    return {
        "style": style,
        "diff": diff,
    }


@register.inclusion_tag("design/tags/code_diff_split.html")
def code_diff_split(diff: SplitDiff, style=""):
    """
    Render a block with a split diff.

    :param diff: The unified diff from the `views.diff.unified_diff` function.
    :param style: Additional classes to add to the diff block.
    """
    return {
        "style": style,
        "diff": diff,
    }


@register.inclusion_tag("design/tags/code_diff_changes.html")
def code_diff_changes(diff: DiffResult, style=""):
    """
    Render a bar that displays the number of changes visually.

    :param diff: The unified diff from the `views.diff.unified_diff` function.
    :param style: Additional classes to be added to the bar.
    """
    return {
        "style": style,
        "diff": diff,
    }


@register.inclusion_tag("design/tags/code_diff_collapse_buttons.html")
def code_diff_collapse_buttons(diff: DiffResult, style=""):
    """
    Render two buttons to expand or collapse all hidden hunks in the diff.

    :param diff: The unified diff from the `views.diff.unified_diff` function.
    :param style: Additional classes to be added to the buttons.
    """
    return {
        "style": style,
        "diff": diff,
    }


@register.inclusion_tag("design/tags/code_editor.html", takes_context=True)
def code_editor(
    context: RenderContext,
    form_field_name: str,
    syntax_format: str = "",
    initial_text: str = "",
    line_numbers_enabled: bool = False,
    first_line_number: int = 1,
    style: str = "",
):
    """
    Use this tage to integrate a code editor as a form element.

    If you work with a code editor, best to use `enctype="multipart/form-data"` to submit the contents of the
    code editor.

    :param context: The render context.
    :param form_field_name: The name of the form field where the text field contents are submitted.
    :param syntax_format: The syntax of the code.
    :param initial_text: The initial text for the editor
    :param line_numbers_enabled: If the line numbers are displayed.
    :param first_line_number: The first line number to display in the editor.
    :param style: A list of CSS classes added to the editor element.
    """
    removed_last_newline = False
    if initial_text.endswith("\n"):
        initial_text = initial_text[:-1]
        removed_last_newline = True
    initial_text_base64 = base64.standard_b64encode(initial_text.encode()).decode()
    include_url = static("design/js/editor.bundle.js")
    hidden_field_id = f"ece_{form_field_name}_field"
    editor_id = f"ece_{form_field_name}_editor"
    data_id = f"ece_{form_field_name}_data"
    js_context = {
        "hidden_field_id": hidden_field_id,
        "editor_id": editor_id,
        "data_id": data_id,
        "field_name": form_field_name,
        "style": style,
        "editor_data": {
            "initial_text_base64": initial_text_base64,
            "syntax_format": syntax_format,
            "line_numbers_enabled": line_numbers_enabled,
            "first_line_number": first_line_number,
            "removed_last_newline": removed_last_newline,
        },
    }
    code = render_to_string("design/tags/code_editor.js", js_context)
    page_end_scripts(context).add_code(code)
    page_end_scripts(context).add_include_once(include_url)
    return js_context
