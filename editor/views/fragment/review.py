#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum

from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend.enums import ReviewState
from design.views.action import ActionHandlerResponse
from design.views.diff import unified_diff, split_diff
from editor.views.fragment.base import FragmentViewBase
from editor.views.session import SESSION_DIFF_MODE


class DiffMode(enum.StrEnum):
    UNIFIED = "unified"
    SPLIT = "split"


class FragmentReviewView(FragmentViewBase):
    template_name = "editor/fragment/review/index.html"

    @transaction.atomic()
    def handle_copy_source(self) -> ActionHandlerResponse:
        if self.fragment.has_edit:
            return None
        self.fragment.set_edit_text(self.fragment.text)

    @transaction.atomic()
    def handle_new_edit(self) -> ActionHandlerResponse:
        if self.fragment.has_edit:
            return None  # The wrong method was called.
        match self.action_value:
            case "source_text":
                new_text = str(self.fragment.text)
            case "transformation_text" if self.fragment.transformation is not None:
                new_text = str(self.fragment.transformation.text)
            case "transformation_output" if self.fragment.transformation is not None:
                new_text = str(self.fragment.transformation.output)
            case "":
                new_text = ""
            case _:
                return None  # ???
        self.fragment.set_edit_text(new_text, notes="")
        return reverse("fragment_edit", kwargs={"pk": self.fragment.pk})

    @transaction.atomic()
    def handle_revert(self):
        if self.action_value == "all" or self.action_value == "edit":
            if self.fragment.has_edit:
                self.fragment.delete_edit()
        if self.action_value == "all" or self.action_value == "transformation":
            if self.fragment.has_transformation:
                self.fragment.delete_transformation()
        self.fragment.save()

    def handle_diff_mode(self) -> ActionHandlerResponse:
        try:
            self.diff_mode = DiffMode(self.action_value)
        except ValueError:
            pass
        return None

    @property
    def diff_mode(self):
        try:
            diff_mode = DiffMode(self.request.session.get(SESSION_DIFF_MODE, "unified"))
        except ValueError:
            diff_mode = DiffMode.UNIFIED
        return diff_mode

    @diff_mode.setter
    def diff_mode(self, diff_mode: DiffMode):
        self.request.session[SESSION_DIFF_MODE] = diff_mode.value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.fragment.text
        first_line_number = self.fragment.first_line_number
        if self.has_edit:
            destination = self.fragment.edit.text
            dst_label = _("Edit")
        elif self.has_transformation:
            destination = self.fragment.transformation.text
            dst_label = _("Transformation")
        else:
            destination = source
            dst_label = _("Source")
        if self.diff_mode == DiffMode.UNIFIED:
            context["diff"] = unified_diff(
                source, destination, src_line=first_line_number, src_label=_("Source"), dst_label=dst_label
            )
        else:
            context["diff"] = split_diff(
                source, destination, src_line=first_line_number, src_label=_("Source"), dst_label=dst_label
            )
        context["diff_mode"] = self.diff_mode
        return context
