#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django import template

register = template.Library()


@register.inclusion_tag("editor/tags/node_row.html")
def editor_node_row(node: "DocumentTreeNode"):
    return {
        "node": node,
        "levels": range(node.level),
        "alternate_background": (node.index % 2 == 0),
    }


@register.simple_tag(takes_context=True)
def editor_project_edit_disable(context):
    """
    Shortcut to disable elements when `is_edit_allowed()` on `project` is `False`.
    Requires variable `project` in the current context.
    """
    if "project" not in context:
        raise ValueError("Tag requires variable `project` in context.")
    if context["project"].can_be_edited:
        return ""
    return " disabled"
