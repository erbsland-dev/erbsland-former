#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
from django.contrib.auth.models import User

from backend.management.commands.base.add_user_base import AddUserCommand


class Command(AddUserCommand):

    def create_user(self, username: str, email: str, password: str = None) -> User:
        user = super().create_user(username, email, password)
        user.is_staff = True
        return user
