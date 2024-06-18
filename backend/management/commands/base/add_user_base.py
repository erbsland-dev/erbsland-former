#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import re
import secrets
from typing import Tuple

from django.contrib.auth.models import User
from django.core.management import BaseCommand, CommandError
from django.db import transaction


class AddUserCommand(BaseCommand):

    RE_USERNAME = re.compile(r"^[a-zA-Z0-9_-]+$")
    RE_EMAIL = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "username",
            metavar="<username>",
            action="store",
            type=str,
            help="A username, between 4 and 32 characters, letters numbers, underscore.",
        )
        parser.add_argument(
            "email",
            metavar="<email>",
            nargs="?",
            action="store",
            type=str,
            help="The optional email address for the account for password resets.",
        )
        parser.add_argument(
            "--password",
            "-p",
            metavar="<password>",
            type=str,
            help="The optional password for the account, if you omit the password, a secure one is created.",
        )
        parser.add_argument(
            "--initial-setup",
            "-i",
            action="store_true",
            help="If set, the user or admin is only added to the database if there are no other in the database.",
        )
        parser.add_argument(
            "--silent", "-s", action="store_true", help="Do not show the created user details on the console."
        )

    def check_input(self, **options) -> Tuple[str, str, str]:
        username = options["username"]
        if 4 > len(username) > 32:
            raise CommandError(f"Username must be between 4 and 32 characters long.")
        if not self.RE_USERNAME.match(username):
            raise CommandError(f"Username must only contain alphanumeric characters, underscores or hyphens.")
        email = options.get("email") or ""
        if email and not self.RE_EMAIL.match(email):
            raise CommandError(f"The email address seems not to be valid.")
        password = options.get("password") or ""
        if not password:
            password = secrets.token_urlsafe(32)
        if len(password) < 16:
            raise CommandError(f"Password must be at least 16 characters long.")
        return username, email, password

    def is_staff(self):
        return False

    def create_user(self, username: str, email: str, password: str = None) -> User:
        with transaction.atomic():
            if User.objects.filter(username=username).exists():
                raise CommandError(f"User {username} already exists in the database.")
            return User.objects.create_user(username=username, email=email, password=password, is_staff=self.is_staff())

    def print_success_message(self, user: User, password: str):
        print(f"Successfully created user with id={user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Password: {password}")
        print(f"Is Admin: {'Yes' if user.is_staff else 'No'}")

    def handle(self, *args, **options):
        is_silent = options.get("silent", False)
        if options["initial_setup"]:
            if User.objects.filter(is_staff=self.is_staff()).exists():
                if not is_silent:
                    print("Ignoring this command, because there are existing user definitions in the database.")
                exit(0)
        username, email, password = self.check_input(**options)
        user = self.create_user(username, email, password)
        if options.get("password"):
            password = "********"  # Hide password from output if it was provided via command line.
        if not is_silent:
            self.print_success_message(user, password)
