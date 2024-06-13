#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .content import Content


class ContentUser(models.Model):
    """
    Abstract base class for all content users.
    """

    content = models.ForeignKey(Content, null=True, on_delete=models.SET_NULL, related_name="+")
    """The source content as imported or copied from another revision."""

    @property
    def text(self):
        """Access the text content for this object."""
        if self.content is None:
            return ""
        return self.content.text

    def _set_content(self, new_content: Optional[Content], *, allocate_new_content: bool = True):
        """
        Replace the content with another one or None.

        :param new_content: The new content or None
        :param allocate_new_content: If the new content should be allocated.
        """
        if self.content is None and new_content is None:
            return  # Ignore this call if there will be no change.
        if self.content is not None and new_content is not None and self.content.pk == new_content.pk:
            return  # Ignore this call if there will be no change.
        if self.content is not None:
            self.content.release()
        self.content = new_content
        if allocate_new_content and self.content is not None:
            self.content.allocate()
        self.save()

    def set_text(self, text: str, existing_content: list[Content] = None):
        """
        Set the text content for this object, reusing existing content if possible.

        :param text: The text to set or update.
        :param existing_content: Existing content blocks to consider.
        """
        # If there is no difference, keep everything as it is.
        if self.text == text:
            return
        # If new text is empty, remove the existing content.
        if text == "":
            self._set_content(None)
            return
        # Find matching blocks for the new text.
        matching_content = None
        if existing_content:
            for content in existing_content:
                if content is not None and content.text == text:
                    matching_content = content
        # In case we have existing content that matches the text.
        if matching_content is not None:
            self._set_content(matching_content)
            return
        # If we have exclusive content, we can change its text.
        if self.content is not None and not self.content.is_shared:
            self.content.text = text
            self.content.save()
            return
        # In any other case, assign a new content block.
        self._set_content(Content.objects.create(text=text), allocate_new_content=False)

    class Meta:
        abstract = True
