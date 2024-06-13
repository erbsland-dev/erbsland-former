#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from design.views.assistant.step_definition import AssistantStepEnumType
from design.views.assistant.steps_base import AssistantStepsBase

AssistantModelType = TypeVar("AssistantModelType", bound=models.Model)
AssistantStepsType = TypeVar("AssistantStepsType", bound=AssistantStepsBase)


class AssistantMixin(ABC, Generic[AssistantStepsType, AssistantStepEnumType, AssistantModelType]):
    """
    A mixin that provides common functionality for all assistant views.
    """

    steps: AssistantStepsType = None
    """Overwrite this with the predefined list of steps for an assistant."""

    stop_page_name: str = None
    """Overwrite to set a different stop page name."""

    intro_text: str = ""
    """Overwrite to add shot intro text at the begin of the assistant page."""

    assistant_name: str = None
    """The name of the assistant, used in the database and as prefix for the page names."""

    assistant_step_enum: type[AssistantStepEnumType] = None
    """The enum class for the assistant step."""

    assistant_display_name: str = None
    """The short name, like 'Ingest' for the assistant. Used as page prefix and on the stop button."""

    assistant_model: type[AssistantModelType] = None
    """The model class for the assistant to be used."""

    def __init__(self, *args, **kwargs):
        self._assistant: Optional[AssistantModelType] = None
        super().__init__(*args, **kwargs)

    def get_steps(self) -> AssistantStepsType:
        if self.steps is None:
            raise ValueError("No steps defined")
        return self.steps

    def get_stop_page_name(self) -> Optional[str]:
        """Get the name for the stop/cancel page in the assistant."""
        return self.stop_page_name

    def get_intro_text(self) -> str:
        return self.intro_text

    def get_assistant_name(self) -> str:
        return self.assistant_name

    def get_assistant_step_enum(self) -> type[AssistantStepEnumType]:
        return self.assistant_step_enum

    def get_assistant_display_name(self) -> str:
        return self.assistant_display_name

    def get_assistant_model(self) -> type[AssistantModelType]:
        return self.assistant_model

    def initialize_db_objects(self) -> Optional[HttpResponse]:
        if response := super().initialize_db_objects():
            return response
        try:
            self._assistant = self.get_assistant()
        except ObjectDoesNotExist:
            if self.is_assistant_required():
                raise Http404(_("The requested assistant was not found."))
        return None

    @property
    def assistant(self) -> AssistantModelType:
        return self._assistant

    @abstractmethod
    def get_assistant(self) -> Optional[AssistantModelType]:
        pass

    def is_assistant_required(self) -> bool:
        """
        If an existing assistant is required for this view..
        """
        return True

    def get_current_step_value(self) -> AssistantStepEnumType:
        if self.assistant:
            return self.get_assistant_step_enum()(self.assistant.step)
        return list(self.get_assistant_step_enum())[0]

    def get_step_page_name(self, value: AssistantStepEnumType) -> str:
        """Get the page name for the given step value."""
        return self.get_steps().get_page_name(value)

    def get_step_label(self, value: AssistantStepEnumType) -> str:
        """Get the label for the given step value."""
        return self.get_steps().get_label(value)

    def get_kwargs_for_step_url(self) -> Optional[dict]:
        """Get the kwargs that are added to the URL when resolving step page names."""
        return None

    def get_step_url(self, value: AssistantStepEnumType) -> str:
        """Resolve the URL for the given step value."""
        return reverse(self.get_step_page_name(value), kwargs=self.get_kwargs_for_step_url())

    def get_stop_url(self) -> str:
        """Resolve the URL for the stop page for the cancel or stop button of an assistant."""
        stop_page_name = self.get_stop_page_name()
        if stop_page_name:
            return reverse(self.get_stop_page_name(), kwargs=self.get_kwargs_for_step_url())
        return ""

    def get_success_url(self):
        return self.get_step_url(self.get_current_step_value())

    def get_form_cancel_text(self) -> str:
        if self.assistant:
            return _("Stop")
        return _("Back")

    def get_form_cancel_url(self) -> str:
        return self.get_stop_url()

    def get_form_cancel_icon(self) -> str:
        if self.assistant:
            return "stop"
        return "arrow-left"

    def get_page_title_prefix(self) -> str:
        if self.get_assistant_display_name() is None:
            raise NotImplementedError("Please define `assistant_display_name`.")
        return self.get_assistant_display_name()

    def get_page_title(self) -> str:
        return self.get_step_label(self.get_current_step_value())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        step_value = self.get_current_step_value()
        context.update(
            {
                "step_value_name": step_value.name,
                "step_definitions": self.get_steps().get_step_definitions(),
                "intro_text": self.get_intro_text(),
            }
        )
        if self.assistant:
            context["assistant"] = self.assistant
            try:
                context["task"] = self.assistant.task
            except ObjectDoesNotExist:
                pass
        return context
