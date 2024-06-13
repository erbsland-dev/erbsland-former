#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from design.views.breadcrumbs import Breadcrumb
from editor.views.fragment.base import FragmentViewBase


class FragmentDetailsView(FragmentViewBase):
    template_name = "editor/fragment/details/index.html"

    def get_breadcrumbs_title(self) -> str:
        return _("Details")

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append(
            Breadcrumb(super().get_breadcrumbs_title(), reverse("fragment", kwargs={"pk": self.fragment.pk}))
        )
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
