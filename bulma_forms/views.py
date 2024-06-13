#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


class BulmaFormsMixin:
    """
    This mixin simplifies the customization for the forms that are rendered using this module.
    """

    form_submit_text = ""
    form_submit_class = ""
    form_submit_icon = ""
    form_cancel_url = ""
    form_cancel_page = ""
    form_cancel_text = ""
    form_cancel_class = ""
    form_cancel_icon = ""

    _FORM_FIELD_NAMES = [
        "submit_text",
        "submit_class",
        "submit_icon",
        "cancel_url",
        "cancel_page",
        "cancel_class",
        "cancel_text",
        "cancel_icon",
    ]

    def get_form_submit_text(self) -> str:
        """Get the optional submit text for the displayed form."""
        return self.form_submit_text

    def get_form_submit_class(self) -> str:
        return self.form_submit_class

    def get_form_submit_icon(self) -> str:
        return self.form_submit_icon

    def get_form_cancel_url(self) -> str:
        return self.form_cancel_url

    def get_form_cancel_page(self) -> str:
        return self.form_cancel_page

    def get_form_cancel_text(self) -> str:
        return self.form_cancel_text

    def get_form_cancel_class(self) -> str:
        return self.form_cancel_class

    def get_form_cancel_icon(self) -> str:
        return self.form_cancel_icon

    def is_form_submit_enabled(self) -> bool:
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only set/overwrite the fields that are specified.
        for name in self._FORM_FIELD_NAMES:
            value = getattr(self, f"get_form_{name}")()
            if value and name not in context:
                context[name] = value
        context["submit_enabled"] = self.is_form_submit_enabled()
        return context
