#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from functools import cached_property

from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend import models
from backend.enums import ReviewState
from backend.models import Fragment
from design.views.action import ActionDetailView, ActionHandlerResponse
from editor.views.session import SESSION_SELECTED_DOCUMENTS
from editor.views.transformation.access import ProjectAccessMixin
from backend.tools.document_tree import DocumentTree, DocumentTreeNodeType


class ProjectDetailView(ProjectAccessMixin, ActionDetailView):
    model = models.Project
    template_name = "editor/project/detail.html"
    page_title_prefix = _("Project")
    page_icon_name = "folder-tree"

    def get_breadcrumbs_title(self) -> str:
        return self.project.name

    @cached_property
    def document_tree(self):
        return DocumentTree(self.revision, with_document_details=True)

    def get_selected_document_ids(self) -> list[int]:
        """
        Get all selected document ids.
        """
        selected_node_indexes: set[int] = set()
        for node_index_str in self.request.POST.getlist("selected_node", default=[]):
            try:
                node_index = int(node_index_str)
                if node_index >= 0:
                    selected_node_indexes.add(node_index)
            except ValueError:
                pass  # Skip invalid values.
        # Filter the flattened list, to get the ids in the selected order.
        document_ids: list[int] = []
        for node in self.document_tree.node_list:
            if node.index not in selected_node_indexes:
                continue
            if node.type != DocumentTreeNodeType.DOCUMENT:
                continue
            document_ids.append(node.document_id)
        return document_ids

    def handle_start_transformation(self) -> ActionHandlerResponse:
        """
        If the user clicks on "Start Transformation", collect the selected files and redirect to
        the transformation assistant.
        """
        # Store them in the session for the transformation setup.
        self.request.session[SESSION_SELECTED_DOCUMENTS] = self.get_selected_document_ids()
        return reverse("transformation", kwargs={"pk": self.project.pk})

    def _handle_review(self, state: ReviewState) -> ActionHandlerResponse:
        fragments = Fragment.objects.filter(document__revision=self.revision, review_state=state.value).order_by(
            "document__path", "position"
        )
        if not fragments.exists():
            return reverse("project_no_pending", kwargs={"pk": self.project.pk})
        fragment = fragments.first()
        return reverse("fragment", kwargs={"pk": fragment.pk})

    def handle_review(self) -> ActionHandlerResponse:
        """
        Handle review actions.
        """
        if self.action_value == "start_pending":
            return self._handle_review(ReviewState.PENDING)
        if self.action_value == "start_rejected":
            return self._handle_review(ReviewState.REJECTED)
        if "_" not in self.action_value:
            return None
        action_state, action_set = self.action_value.split("_", maxsplit=2)
        try:
            new_state = ReviewState[action_state.upper()]
        except KeyError:
            return None
        with transaction.atomic():
            match action_set:
                case "all":
                    Fragment.objects.all().update(review_state=new_state.value)
                case "selected":
                    selected_document_ids = self.get_selected_document_ids()
                    Fragment.objects.filter(document__id__in=selected_document_ids).update(review_state=new_state.value)
                case "unchanged":
                    for fragment in Fragment.objects.all():
                        if not fragment.has_text_changes:
                            fragment.review_state = new_state.value
                            fragment.save()
                case "changed":
                    for fragment in Fragment.objects.all():
                        if fragment.has_text_changes:
                            fragment.review_state = new_state.value
                            fragment.save()
                case _:
                    return None
        return None

    def handle_new_revision(self) -> ActionHandlerResponse:
        return reverse("new_revision_checks", kwargs={"pk": self.project.pk}) + f"?revision={self.revision.number}"

    def handle_export(self) -> ActionHandlerResponse:
        # Store them in the session for the egress setup.
        self.request.session[SESSION_SELECTED_DOCUMENTS] = self.get_selected_document_ids()
        return reverse("egress_setup", kwargs={"pk": self.project.pk}) + f"?revision={self.revision.number}"

    def handle_delete_revision(self) -> ActionHandlerResponse:
        return reverse("revision_delete", kwargs={"pk": self.project.pk, "revision": self.revision.number})

    def handle_edit_revision_label(self) -> ActionHandlerResponse:
        return reverse("revision_edit_label", kwargs={"pk": self.project.pk, "revision": self.revision.number})

    def get_review_buttons(self) -> list:
        selection_sets = [
            (_("Reset All to %(state)s"), "all", "folder-tree"),
            (_("Set Selected to %(state)s"), "selected", "list-check"),
            (_("Set Unchanged to %(state)s"), "unchanged", "equals"),
            (_("Set Changed to %(state)s"), "changed", "not-equal"),
        ]
        button_fields = []
        for selection_set in selection_sets:
            for state in ReviewState:
                button_fields.append(
                    {
                        "label": selection_set[0] % {"state": state.label},
                        "color_class": f"has-text-{state.name.lower()}-dark",
                        "action_value": f"{state.name.lower()}_{selection_set[1]}",
                        "selection_icon": selection_set[2],
                        "state_icon": state.icon_name,
                    }
                )
        return button_fields

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_states = self.revision.review_states()
        transformation_states = self.revision.transformation_states()
        main_action = ""
        if not self.is_latest_revision:
            pass  # No default action if we are viewing an old version.
        elif self.document_tree.has_no_documents:
            main_action = "import"
        elif not self.revision.transformations.exists():
            main_action = "transformation"
        elif review_states.has_pending_reviews or review_states.has_rejected_reviews:
            main_action = "review"
        else:
            main_action = "new_revision_and_export"
        latest_revisions = self.project.get_revisions(5)
        context.update(
            {
                "latest_revisions": latest_revisions,
                "review_states": review_states,
                "transformation_states": transformation_states,
                "main_action": main_action,
                "is_latest_revision": self.is_latest_revision,
                "has_pending_reviews": review_states.has_pending_reviews,
                "has_rejected_reviews": review_states.has_rejected_reviews,
                "review_buttons": self.get_review_buttons(),
                "document_tree": self.document_tree,
                "disable_import": (self.has_unfinished_tasks or not self.is_latest_revision),
                "disable_transformation": (self.has_unfinished_tasks or not self.is_latest_revision),
                "disable_review": self.document_tree.has_no_documents,
                "disable_new_revision": self.has_unfinished_tasks,
                "disable_export": self.has_unfinished_tasks,
            }
        )
        return context
