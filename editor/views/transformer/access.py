#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.urls import reverse

from backend.models import TransformerProfile
from design.views.breadcrumbs import Breadcrumb
from django.utils.translation import gettext_lazy as _


class TransformerAccessMixin:
    """
    A mixin that provides and verifies access to a transformer profile.
    """

    def __init__(self, *args, **kwargs):
        self.request: Optional[HttpRequest] = None
        self.args: Optional[list] = None
        self.kwargs: Optional[dict] = None
        self._transformer_profile: Optional[TransformerProfile] = None
        super().__init__(*args, **kwargs)

    def check_access_rights(self) -> Optional[HttpResponse]:
        """
        Test is the currently logged-in user has access to this project.
        """
        if not self.request.user or not self.request.user.is_authenticated:
            return HttpResponseForbidden("You don't have the required permission.")
        if not self.transformer_profile.can_user_edit(self.request.user):
            return HttpResponseForbidden("You don't have the required permission.")
        return None

    def initialize_db_objects(self) -> Optional[HttpResponse]:
        """
        Initialize all database objects
        """
        try:
            self._transformer_profile = self.get_transformer_profile()
        except ObjectDoesNotExist:
            return HttpResponseNotFound(_("The requested transformer profile was not found."))
        return None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if response := self.initialize_db_objects():
            return response
        if response := self.check_access_rights():
            return response
        return super().dispatch(request, *args, **kwargs)

    def get_transformer_profile(self) -> TransformerProfile:
        return TransformerProfile.objects.get(pk=self.kwargs["pk"])

    @property
    def transformer_profile(self) -> TransformerProfile:
        return self._transformer_profile

    def get_object(self, queryset=None):
        # Replace the get object method for project access subclasses.
        return self.transformer_profile

    def get_context_data(self, **kwargs):
        # Add the context variables to access the project and revision.
        context = super().get_context_data(**kwargs)
        context.update({"transformer_profile": self.transformer_profile})
        return context

    def get_page_title(self) -> str:
        return self.transformer_profile.profile_name

    def get_breadcrumbs_title(self) -> str:
        return self.transformer_profile.profile_name

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return [Breadcrumb(_("Transformer Profiles"), reverse("transformer"))]
