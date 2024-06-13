#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cache, cached_property
from typing import Generic, Optional, Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Count
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend.enums import TransformerStatus
from backend.models import Document, Fragment
from backend.syntax_handler import syntax_manager
from design.views.assistant.mixin import AssistantModelType, AssistantStepsType, AssistantMixin
from design.views.assistant.step_definition import AssistantStepEnumType
from design.views.breadcrumbs import Breadcrumb
from design.views.checks import CheckList, CheckState
from editor.views.session import SESSION_SELECTED_DOCUMENTS


class ProjectAssistantMixin(AssistantMixin, Generic[AssistantStepsType, AssistantStepEnumType, AssistantModelType]):

    @cache
    def get_assistant(self) -> Optional[AssistantModelType]:
        if self.get_assistant_model() is None or self.get_assistant_step_enum() is None:
            raise NotImplementedError("Please define `assistant_model` and `assistant_step_enum`.")
        if not hasattr(self, "project") or self.project is None:
            raise NotImplementedError("This mix-in is used in the wrong context.")
        field_name = self.get_assistant_model().__name__.lower()
        try:
            return getattr(self.project.assistant, field_name)
        except ObjectDoesNotExist:
            return None

    def get_kwargs_for_step_url(self) -> dict:
        return {"pk": self.project.pk}

    def get_form_cancel_url(self) -> str:
        if self.assistant:
            return reverse(f"{self.get_assistant_name()}_stop", kwargs=self.get_kwargs_for_step_url())
        return self.get_project_url()  # Assuming this method will exist.

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return [Breadcrumb(self.project.name, self.get_project_url())]

    def create_assistant_instance(self, *, step: AssistantStepEnumType = None, **kwargs) -> None:
        """
        Create a new instance of the assistant model.

        - The new instance is accessible via `self.assistant`.
        - No transactions are committed to the database.

        :param step: The initial assistant step. `None` for the first one.
        :param kwargs: Additional keyword arguments are added to the `create` method.
        """
        if self.project.has_unfinished_tasks():
            raise ValueError(_("There is already a task running for this project."))
        if self.assistant:
            raise ValueError("Internal problem: There is already an assistant instance assigned.")
        try:
            # Check if another assistant is running.
            assistant = self.project.assistant
            raise ValueError(
                _("There is already an %(assistant_name)s assistant running for this project.")
                % {"assistant_name": assistant.get_verbose_assistant_name()}
            )
        except ObjectDoesNotExist:
            pass  # This is ok! No assistant must be assigned to the project.
        if step is None:
            step = self.get_current_step_value()
        self._assistant = self.get_assistant_model().objects.create(
            project=self.project,
            revision=self.revision,
            user=self.request.user,
            assistant_name=self.get_assistant_name(),
            step=step,
            **kwargs,
        )

    def _get_selected_documents_from_session(self) -> QuerySet[Document]:
        """
        Get all selected documents from the user session.
        """
        selected_documents = self.request.session.get(SESSION_SELECTED_DOCUMENTS, [])
        return Document.objects.filter(revision=self.revision, id__in=selected_documents).order_by(Lower("path"))

    @cached_property
    def selected_documents(self) -> QuerySet[Document]:
        if not self.assistant:
            return self._get_selected_documents_from_session()
        return self.assistant.get_selected_documents()

    @cached_property
    def selected_document_count_text(self) -> str:
        if isinstance(self.selected_documents, QuerySet):
            selected_document_count = self.selected_documents.count()
        else:
            selected_document_count = len(self.selected_documents)
        if selected_document_count == 0:
            text = _("No Documents")
        elif selected_document_count == self.revision.documents.count():
            text = _("All Documents")
        elif selected_document_count == 1:
            text = _("One Document")
        else:
            text = _("%(count)d Documents") % {"count": selected_document_count}
        return text

    @cached_property
    def selected_fragment_count(self) -> int:
        return Fragment.objects.filter(document__in=self.selected_documents).count()

    @cached_property
    def selected_fragment_count_text(self) -> str:
        selected_fragment_count = self.selected_fragment_count
        if selected_fragment_count == 0:
            text = _("No Fragments")
        elif selected_fragment_count == 1:
            text = _("One Fragment")
        else:
            text = _("%(count)d Fragments") % {"count": selected_fragment_count}
        return text

    @cached_property
    def selected_syntax_list(self) -> list[Tuple[str, int]]:
        selected_syntax = (
            self.selected_documents.values("document_syntax")
            .annotate(count=Count("document_syntax"))
            .order_by("document_syntax")
        )
        selected_syntax_list: list[Tuple[str, int]] = []
        for entry in selected_syntax:
            selected_syntax_list.append((syntax_manager.verbose_name(entry["document_syntax"]), entry["count"]))
        return selected_syntax_list

    @cached_property
    def selected_revision_text(self) -> str:
        if self.is_latest_revision:
            text = _("Latest Revision")
        else:
            text = _("Revision %(revision_number)d") % {"revision_number": self.revision.number}
        return text

    @cached_property
    def check_results(self) -> CheckList:
        """
        Basic checks performed before any task can be run.

        Overwrite `add_checks()` to add your own check in a subclass.
        """
        result = CheckList()
        if not self.revision.documents.exists():
            result.add(CheckState.ERROR, _("The revision doesn't include any documents."))
        self.add_checks(result)
        return result

    def add_checks(self, check_list: CheckList) -> None:
        """
        Overwrite this method to add more checks.

        :param check_list: The checklist object where you add your checks.
        """
        pass

    def add_selected_document_check(self, check_list: CheckList) -> None:
        if not self.selected_documents.exists():
            check_list.add(CheckState.ERROR, _("No documents have been selected."))

    def add_latest_revision_warning(self, check_list: CheckList) -> None:
        if self.revision.is_latest:
            check_list.add(CheckState.OK, _("You selected the latest revision for the operation."))
        else:
            check_list.add(CheckState.WARNING, _("Please, note you selected an older revision."))

    def add_review_check(self, check_list: CheckList) -> None:
        review_states = self.revision.review_states()
        if review_states.has_rejected_reviews:
            check_list.add(CheckState.WARNING, _("The selected revision contains rejected reviews."))
        elif review_states.has_pending_reviews:
            check_list.add(CheckState.WARNING, _("The selected revision contains text fragments awaiting approval."))
        else:
            check_list.add(CheckState.OK, _("All processed fragments have been reviewed and accepted."))

    def add_transformer_failure_check(self, check_list: CheckList) -> None:
        transformer_failure_count = self.revision.documents.filter(
            fragments__edit__isnull=True,
            fragments__transformation__isnull=False,
            fragments__transformation__status=TransformerStatus.FAILURE.value,
        ).count()
        if transformer_failure_count > 0:
            check_list.add(
                CheckState.WARNING,
                _("%(count)d document has failed transformations and require edits.")
                % {"count": transformer_failure_count},
            )
        else:
            check_list.add(CheckState.OK, _("No fragments have unedited failed transformations."))

    def add_unprocessed_fragments_check(self, check_list: CheckList) -> None:
        unprocessed_fragment_count = Fragment.objects.filter(edit__isnull=True, transformation__isnull=True).count()
        if unprocessed_fragment_count > 0:
            check_list.add(
                CheckState.WARNING,
                _("There are %(count)d unprocessed document fragments.") % {"count": unprocessed_fragment_count},
            )
        else:
            check_list.add(CheckState.OK, _("All document fragments have been processed."))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use `lamda`s to calculate these values only when needed by the template.
        context.update(
            {
                "selected_documents": lambda: self.selected_documents,
                "selected_document_count": lambda: self.selected_documents.count(),
                "selected_document_count_text": lambda: self.selected_document_count_text,
                "selected_fragment_count": lambda: self.selected_fragment_count,
                "selected_fragment_count_text": lambda: self.selected_fragment_count_text,
                "selected_syntax_list": lambda: self.selected_syntax_list,
                "selected_revision": lambda: self.selected_revision_text,
                "checks": lambda: self.check_results,
            }
        )
        return context
