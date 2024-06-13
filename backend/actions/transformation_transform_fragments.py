#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from backend.actions.transformation_base import TransformationBase
from backend.enums import TransformerStatus
from backend.enums.transformation_step import TransformationStep
from backend.models import Transformation, Fragment, Document
from backend.transformer import TransformerBase
from backend.transformer.context import TransformerDocumentContext, TransformerFragmentContext
from backend.transformer.error import TransformerError
from backend.transformer.fragment_access import FragmentAccess
from backend.transformer.manager import transformer_manager
from backend.transformer.processor import Processor
from backend.transformer.result import ProcessorResult
from tasks.actions import ActionError
from tasks.actions.exception import ActionStoppedByUser
from tasks.actions.status import TaskStatusField


class _DocumentContext(TransformerDocumentContext):
    def __init__(self, document: Document):
        self._document_name = document.name
        self._document_path = document.path
        self._document_folder = document.folder
        self._document_syntax = document.document_syntax

    @property
    def document_name(self) -> str:
        return self._document_name

    @property
    def document_folder(self) -> str:
        return self._document_folder

    @property
    def document_path(self) -> str:
        return self._document_path

    @property
    def document_syntax(self) -> str:
        return self._document_syntax


class _FragmentContext(TransformerFragmentContext):
    def __init__(self, fragments: list[Fragment], current_index: int, fragment: Fragment):
        self._fragments = fragments
        self._current_index = current_index
        self._fragment = fragment
        self._document_name = fragment.document.name
        self._document_path = fragment.document.path
        self._document_folder = fragment.document.folder
        self._document_syntax = fragment.document.document_syntax

    @property
    def document_name(self) -> str:
        return self._document_name

    @property
    def document_folder(self) -> str:
        return self._document_folder

    @property
    def document_path(self) -> str:
        return self._document_path

    @property
    def document_syntax(self) -> str:
        return self._document_syntax

    @property
    def fragment_index(self) -> int:
        return self._fragment.position

    @property
    def fragment_count(self) -> int:
        return self._fragment.document.fragments.count()

    @property
    def fragment_context(self) -> dict[str, str]:
        return self._fragment.context

    @property
    def processed_count(self) -> int:
        return self._current_index

    def get_processed(self, steps_back: int = 0) -> Optional[FragmentAccess]:
        index = self._current_index - steps_back - 1
        if index < 0 or index >= self._current_index:
            return None
        return self._fragments[index]

    @property
    def previous_count(self) -> int:
        return self._fragment.position

    def get_previous(self, steps_back: int = 0) -> Optional[FragmentAccess]:
        if steps_back < 0 or steps_back >= self._fragment.position:
            return None
        try:
            return self._fragment.document.fragments.get(position=self._fragment.position - steps_back - 1)
        except ObjectDoesNotExist:
            return None


STATUS_DOCUMENT_COUNT = "document_count"
STATUS_FRAGMENT_COUNT = "fragment_count"
STATUS_CHANGED_FRAGMENT_COUNT = "changed_fragment_count"
STATUS_FAILURE_COUNT = "failure_count"


class TransformationTransformFragments(TransformationBase):
    name = "transform_fragments"
    progress_title = _("Transform Fragments")
    progress_subject = _("Transformation")
    status_fields = [
        TaskStatusField(STATUS_DOCUMENT_COUNT, _("Processed Documents"), "—", "file-circle-check"),
        TaskStatusField(STATUS_FRAGMENT_COUNT, _("Processed Fragments"), "—", "list-check"),
        TaskStatusField(STATUS_CHANGED_FRAGMENT_COUNT, _("Changed Fragments"), "—", "pen"),
        TaskStatusField(STATUS_FAILURE_COUNT, _("Failed Transformations"), "—", "xmark"),
    ]

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)
        self.transformer: Optional[TransformerBase] = None  # The transformer entry in the project.
        self.processor: Optional[Processor] = None  # The processor instance for the transformer.
        self.fragments: list[Fragment] = []  # The list of fragments to process.
        self._last_document: Optional[Document] = None  # The last processed document.
        self.document_count: int = 0
        self.fragment_count: int = 0
        self.changed_fragment_count: int = 0
        self.success_count: int = 0
        self.failure_count: int = 0
        self.consecutive_failure_count: int = 0

    def _status_values(self):
        status_values = {
            STATUS_DOCUMENT_COUNT: f"{self.document_count}",
            STATUS_FRAGMENT_COUNT: f"{self.fragment_count} / {len(self.fragments)}",
            STATUS_CHANGED_FRAGMENT_COUNT: f"{self.changed_fragment_count}",
            STATUS_FAILURE_COUNT: f"{self.failure_count}",
        }
        if self.processor:
            status_values.update(self.processor.get_status_values())
        return status_values

    def run(self, input_data: dict) -> None:
        self.log_info(_("Preparing the transformation."))
        try:
            with transaction.atomic():
                self.set_progress(0.0, 100.0, _("Initializing the transformation"))
                self.set_db_object_from_input_data(input_data)
                if self.transformation_assistant.step != TransformationStep.TRANSFORMATION_RUNNING:
                    raise ActionError(_("The transformation operation is in the wrong state."))
                self.create_transformation()
                self.create_processor()
                self.initialize_processor()
                self.create_fragment_list()
                try:
                    self.transform_fragments()
                except TransformerError as error:
                    if self.transformation_assistant.rollback_on_failure:
                        raise
                    self.transformation_assistant.failure_reason = str(error)
                except ActionStoppedByUser:
                    if self.transformation_assistant.rollback_on_failure:
                        raise
                    self.transformation_assistant.failure_reason = _("The transformation was stopped by the user.")
                self.transformation.statistics = {
                    "documents": self.document_count,
                    "fragments": self.fragment_count,
                    "changed_fragments": self.changed_fragment_count,
                    "failures": self.failure_count,
                    **self.processor.get_statistics(),
                }
                self.transformation.save()
                self.transformation_assistant.step = TransformationStep.DONE
                self.transformation_assistant.transformation = self.transformation
                self.transformation_assistant.statistics = self.transformation.statistics
                self.transformation_assistant.save()
            self.set_progress(100.0, 100.0, _("Successfully transformed all fragments."), self._status_values())
            self.log_info(_("Successfully transformed all fragments."))
        except Exception:
            # In case of any error, go back to the setup step.
            self.log_error(_("Failed to transform the fragments."))
            if self.transformation_assistant:
                with transaction.atomic():
                    self.transformation_assistant.step = TransformationStep.PREVIEW
                    self.transformation_assistant.save()
            raise

    def get_transformer(self) -> TransformerBase:
        """
        Get the transformer which was selected by the assistant.
        """
        return transformer_manager.get_transformer(self.transformation_assistant.profile.transformer_name)

    def create_transformation(self):
        """
        Create the transformation and store all
        """
        self.transformer = self.get_transformer()
        self.log_info(
            _("Initialize the transformer '%(transformer_verbose_name)s' with the configuration from the profile.")
            % {"transformer_verbose_name": self.transformer.get_verbose_name()}
        )
        profile = self.transformation_assistant.profile
        transformer_name = profile.transformer_name
        self.transformation = Transformation.objects.create(
            revision=self.transformation_assistant.revision,
            transformer_name=transformer_name,
            profile=profile,
            profile_name=profile.profile_name,
            version=self.transformer.version,
            configuration=profile.configuration,
        )

    def create_processor(self):
        """
        Create and prepare the processor instance.
        """
        self.log_info(_("Create the processor instance with the configuration from the profile."))
        profile = self.transformation_assistant.profile
        transformer_name = profile.transformer_name
        profile_settings = profile.get_settings()
        user_settings = None
        try:
            settings = self.transformation_assistant.user.settings
            user_settings = settings.transformer_settings.get(transformer_name=transformer_name).get_settings()
        except ObjectDoesNotExist:
            pass  # Having no user user settings is a valid situation.
        if self.transformer.user_settings_handler and user_settings is None:
            # If the transformer requires user settings, but none are defined, use the default settings.
            user_settings = self.transformer.user_settings_handler.get_default()
        processor_class: type[Processor] = self.transformer.get_processor_class()
        self.processor = processor_class(self.task_id, self, profile_settings, user_settings)

    def initialize_processor(self):
        """
        Initialize the processor object
        """
        self.log_info(_("Initialize the processor."))
        self.processor.initialize()

    def create_fragment_list(self):
        """
        Create the definitive list of fragments to process.
        """
        self.fragments = list(self.transformation_assistant.get_selected_fragments().order_by("document", "position"))

    def transform_fragments(self):
        """
        Transform the individual fragments.
        """
        self.log_info(_("Start transforming the fragments"))
        for index, fragment in enumerate(self.fragments):
            text = _("Transforming fragment %(index)d from %(count)d") % {
                "index": index + 1,
                "count": len(self.fragments),
            }
            self.log_info(text)
            self.set_progress(float(index), float(len(self.fragments)), text, self._status_values())
            self.transform_fragment(fragment, index)
        # Make sure the last document end is signalled to the processor.
        if self._last_document:
            document_context = self.create_document_context(self._last_document)
            self.processor.document_end(document_context)

    def transform_fragment(self, fragment: Fragment, index: int):
        """
        Transform one fragment.

        :param index: The index of the fragment in the list.
        :param fragment: The fragment to transform.
        """
        self._handle_document_change(fragment)
        try:
            fragment_context = self.create_fragment_context(fragment, index)
            result = self.processor.transform(fragment.text, fragment_context)
        except TransformerError as error:
            result = ProcessorResult(
                content="",
                output=error.failure_output or "",
                status=TransformerStatus.FAILURE,
                failure_input=error.failure_input or "",
                failure_reason=str(error),
            )
        # Update the fragment with the transformation result.
        has_changed_text = fragment.set_transformation(
            self.transformation, result, self.transformation_assistant.auto_approve_unchanged
        )
        self._update_counters(has_changed_text, result)

    def _update_counters(self, has_changed_text: bool, result: ProcessorResult) -> None:
        self.fragment_count += 1
        if has_changed_text:
            self.changed_fragment_count += 1
        if result.status == TransformerStatus.FAILURE:
            self.failure_count += 1
            self.consecutive_failure_count += 1
        else:
            self.success_count += 1
            self.consecutive_failure_count = 0
        max_consecutive_failures = self.transformation_assistant.stop_consecutive_failures
        if 0 < max_consecutive_failures <= self.consecutive_failure_count:
            raise TransformerError(
                _("Stopping transformation task because of %(failure_count)d consecutive failures.")
                % {"failure_count": self.consecutive_failure_count}
            )
        max_total_failures = self.transformation_assistant.stop_total_failures
        if 0 < max_total_failures <= self.failure_count:
            raise TransformerError(
                _("Stopping transformation task because %(failure_count)d failures.")
                % {"failure_count": self.failure_count}
            )

    def _handle_document_change(self, fragment: Fragment) -> None:
        """
        Check if the current document changes in the sequence.

        :param fragment: The processed fragment.
        """
        if fragment.document != self._last_document:
            self.document_count += 1
            if self._last_document:
                document_context = self.create_document_context(self._last_document)
                self.processor.document_end(document_context)
            self._last_document = fragment.document
            document_context = self.create_document_context(fragment.document)
            self.processor.document_begin(document_context)

    def create_document_context(self, document: Document) -> TransformerDocumentContext:
        """
        Create a document index for the given document.

        :param document: The document.
        :return: The context for the document.
        """
        return _DocumentContext(document)

    def create_fragment_context(self, fragment: Fragment, index: int) -> TransformerFragmentContext:
        """
        Create a fragment index.

        :param fragment: The fragment.
        :param index: The current index.
        :return: The context for the fragment.
        """
        return _FragmentContext(self.fragments, index, fragment)
