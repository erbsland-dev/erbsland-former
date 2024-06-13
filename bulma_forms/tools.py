#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.forms import Form

BULMA_LEFT_ICON_ATTR = "bulma_left_icon"


def add_icon_to_field(form: Form, field_name: str, fa_classes: str):
    """
    Add an icon to the field of an existing form.

    :param form: The form.
    :param field_name: The name of the field to change.
    :param fa_classes: The font awesome class names.
    """
    if not isinstance(form, Form):
        raise ValueError("Expected a Django form as first argument.")
    if field_name not in form.fields:
        raise ValueError(f"There is no field `{field_name}` in the form.")
    form.fields[field_name].widget.attrs[BULMA_LEFT_ICON_ATTR] = fa_classes
