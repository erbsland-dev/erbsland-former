#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import enum
from functools import cached_property

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic as generic_views
from django.utils.translation import gettext_lazy as _

from bulma_forms.views import BulmaFormsMixin
from design.views.breadcrumbs import BreadcrumbMixin


class AuthenticationLevel(enum.Enum):
    """
    The authentication level required for a view.
    """

    USER = enum.auto()
    ADMIN = enum.auto()
    SUPERUSER = enum.auto()


class AuthenticationRequiredMixin(LoginRequiredMixin):
    """
    Mixin for views that require authentication.
    """

    login_url = reverse_lazy("login")
    authentication_level = AuthenticationLevel.USER

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.authentication_level == AuthenticationLevel.ADMIN and not (
            request.user.is_staff or request.user.is_superuser
        ):
            return self.handle_no_permission()
        if self.authentication_level == AuthenticationLevel.SUPERUSER and not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DesignMixin(BreadcrumbMixin):
    """
    A mixin that contains all basic elements for the design views.
    """

    pass


class PageView(DesignMixin, AuthenticationRequiredMixin, generic_views.TemplateView):
    """
    Base class for all page views.
    """

    pass


class FormView(BulmaFormsMixin, DesignMixin, AuthenticationRequiredMixin, generic_views.FormView):
    """
    Base class for all form views.
    """

    pass


class ConfirmView(FormView):
    """
    Base class to confirm an action using a modal page.
    """

    class Form(forms.Form):
        pass

    form_class = Form
    template_name = "design/modal/confirm.html"
    form_cancel_url = reverse_lazy("home")
    form_cancel_text = _("Back")
    form_cancel_icon = "arrow-left"
    form_cancel_class = "is-medium"
    form_submit_text = _("Continue")
    form_submit_class = "is-danger is-medium"

    warning_text = _("Are you sure to proceed with this action?")

    def get_warning_text(self) -> str:
        return self.warning_text

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"warning_text": self.get_warning_text()})
        return context


class MessageType(enum.Enum):
    INFORMATION = enum.auto()
    WARNING = enum.auto()


class MessageView(FormView):
    """
    Base class to display warning or information views.
    """

    class Form(forms.Form):
        pass

    form_class = Form
    template_name = "design/modal/message.html"

    message_type = MessageType.INFORMATION
    message_text = "Please report this message to the developer."
    form_button_url = reverse_lazy("home")
    form_button_text = _("OK")

    def get_message_text(self) -> str:
        return self.message_text

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "message_text": self.get_message_text(),
            }
        )
        return context


class CreateView(DesignMixin, AuthenticationRequiredMixin, generic_views.CreateView):
    """
    Base class for all create views.
    """

    pass


class UpdateView(BulmaFormsMixin, DesignMixin, AuthenticationRequiredMixin, generic_views.UpdateView):
    """
    Base class for all update views.
    """

    form_cancel_icon = "arrow-left"
    form_submit_icon = "save"

    def get_form_submit_text(self) -> str:
        return _("Update")


class DeleteView(BulmaFormsMixin, DesignMixin, AuthenticationRequiredMixin, generic_views.DeleteView):
    """
    Base class for all delete-views.
    """

    template_name = "design/modal/confirm.html"
    form_cancel_url = reverse_lazy("home")
    form_cancel_icon = "arrow-left"
    form_cancel_class = "is-medium"
    form_submit_class = "is-danger is-medium"

    def get_page_title_prefix(self) -> str:
        return _("Delete %(object_type_name)s") % self.text_replacements

    def get_object_type_name(self) -> str:
        """
        Get the name of the object type that gets deleted (e.g. Project, Revision, Document).
        """
        return self.model._meta.verbose_name

    def get_object_name(self) -> str:
        """
        Get the name of the object to be displayed in the text and on the delete button.
        """
        return str(self.object)

    @cached_property
    def text_replacements(self):
        """
        Create the text replacements that can be used on the warning text and on the submit button.
        """
        return {"object_type_name": self.get_object_type_name(), "object_name": self.get_object_name()}

    def get_warning_text(self) -> str:
        return (
            _(
                'If you click on "Delete %(object_type_name)s" below, the object will be deleted '
                "permanently, and recovery will not be possible."
            )
            % self.text_replacements
        )

    def get_notification_text(self) -> str:
        return _("Successfully deleted %(object_type_name)s “%(object_name)s”.") % self.text_replacements

    def get_form_submit_text(self) -> str:
        return _("Delete %(object_name)s") % self.text_replacements

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"warning_text": self.get_warning_text()})
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.warning(self.request, self.get_notification_text())
        return result


class DetailView(DesignMixin, AuthenticationRequiredMixin, generic_views.DetailView):
    """
    Base class for all details views.
    """

    pass
