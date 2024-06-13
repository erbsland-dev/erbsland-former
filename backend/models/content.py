#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models


class Content(models.Model):
    """
    The content is a block of text referenced by one or more fragments.

    By having text blocks referenced by ID, fragments can share unchanged text blocks. This not only
    reduces the storage amount required for projects with many revisions, but also makes creating
    revisions extremely fast as only ids are copied, not texts.
    """

    text = models.TextField()
    """The text of the content block."""

    usage_count = models.IntegerField(default=1)
    """The number of usages for this content block."""

    @property
    def is_shared(self):
        return self.usage_count > 1

    @property
    def is_used(self):
        return self.usage_count > 0

    def allocate(self):
        """
        Allocate this content.
        """
        self.usage_count += 1
        self.save()

    def release(self):
        """
        Release this content.
        """
        self.usage_count -= 1
        self.save()
        if not self.is_used:
            self.delete()
