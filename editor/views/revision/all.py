#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from backend.models import Project
from design.views.action import ActionDetailView, ActionHandlerResponse
from design.views.breadcrumbs import Breadcrumb
from editor.views.project import ProjectAccessMixin


@dataclass
class RevisionRow:
    number: int
    predecessor: int
    successors: list[int]
    label: str
    url: str
    has_delete: bool
    tile_name: str = ""
    ins: str = ""
    outs: str = ""


class AllRevisionsView(ProjectAccessMixin, ActionDetailView):
    model = Project
    template_name = "editor/revision/all.html"
    page_title_prefix = _("Project Revisions")
    page_icon_name = "folder-tree"

    def get_breadcrumbs_title(self) -> str:
        return _("All Revisions")

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(self.project.name, self.get_project_url()))
        return breadcrumbs

    def handle_back(self) -> ActionHandlerResponse:
        return self.get_project_url()

    def get_revision_rows(self) -> list[RevisionRow]:
        revisions = self.project.revisions.order_by("-number")

        revision_rows = [
            RevisionRow(
                number=revision.number,
                predecessor=revision.predecessor.number if revision.predecessor else 0,
                successors=list([revision.number for revision in revision.successors.order_by("number")]),
                label=revision.label,
                url=reverse_lazy("project", kwargs={"pk": self.project.pk, "revision": revision.number}),
                has_delete=revision.can_be_deleted,
            )
            for revision in revisions
        ]

        last_number_in_sequence = -1
        for index, row in enumerate(revision_rows):
            if index < len(revision_rows) - 1:
                has_down = row.predecessor == revision_rows[index + 1].number
            else:
                has_down = False

            if row.predecessor > 0 and not has_down:
                row.ins = str(row.predecessor)
            else:
                row.ins = ""
            row.outs = ", ".join(str(n) for n in row.successors if n != last_number_in_sequence)

            has_up = last_number_in_sequence in row.successors
            has_in = bool(row.ins)
            has_out = bool(row.outs)

            directions = (
                direction
                for direction, exists in zip(["up", "down", "in", "out"], [has_up, has_down, has_in, has_out])
                if exists
            )
            row.tile_name = "-".join(directions)
            last_number_in_sequence = row.number
        return revision_rows

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["revision_rows"] = self.get_revision_rows()
        return context
