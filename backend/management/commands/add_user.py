#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import re
import secrets

from django.contrib.auth.models import User
from django.core.management import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):

    RE_USERNAME = re.compile(r"^[a-zA-Z0-9_-]+$")
    RE_EMAIL = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    help = f"""\
        Add a new user to the application. This command automatically generates an initial
        secure password for the user if omitted"""

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("username", metavar="<username>", type=str)
        parser.add_argument("email", metavar="<email>", type=str)
        parser.add_argument("password", nargs="?", metavar="<password>", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        if 4 > len(username) > 32:
            raise CommandError(f"Username must be between 4 and 32 characters long.")
        if not self.RE_USERNAME.match(username):
            raise CommandError(f"Username must only contain alphanumeric characters, underscores or hyphens.")
        email = options["email"]
        if not self.RE_EMAIL.match(email):
            raise CommandError(f"The email address seems not to be valid.")
        password = options["password"]
        if not password:
            password = secrets.token_urlsafe(32)
        if len(password) < 16:
            raise CommandError(f"Password must be at least 16 characters long.")
        with transaction.atomic():
            if User.objects.filter(username=username).exists():
                raise CommandError(f"User {username} already exists in the database.")
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
        print("Successfully created a new user:")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
