#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import re
import shutil
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand, CommandError
from django.db import connection

from backend.models import Project, TransformerProfile


class Command(BaseCommand):
    MIGRATION_DIRS = ["backend", "editor", "tasks"]
    PUBLISHED_REVISION = 1

    help = f"""\
        Recreates all migrations that are newer than revision {PUBLISHED_REVISION}.
        Deletes the existing test database and recreates it with prefilled data. 
        Make sure Django isn't running."""

    def add_arguments(self, parser):
        pass

    def execute_manage_cmd(self, args: list[str]):
        cmd_args = [sys.executable, "manage.py"]
        cmd_args.extend(args)
        print("Running: " + " ".join(cmd_args))
        with subprocess.Popen(cmd_args, stdout=subprocess.PIPE, encoding="utf-8") as process:
            for line in iter(lambda: process.stdout.readline(), ""):
                sys.stdout.write(line)
        if process.returncode != 0:
            raise CommandError("Failed to run the management command.")

    def handle(self, *args, **options):
        # Manually specify the SQLite db to prevent deleting anything useful.
        print("Scanning for new migration files.")
        re_migration_name = re.compile(R"^(\d{4})_.*\.py$")
        if "sqlite3" in settings.DATABASES["default"]["ENGINE"]:
            db_file = settings.BASE_DIR / "db.sqlite3"
            print(f"Deleting SQLITE database file: {db_file}")
            db_file.unlink(missing_ok=True)
        elif "mysql" in settings.DATABASES["default"]["ENGINE"]:
            print("Try to drop all tables in the database.")
            with connection.cursor() as cursor:
                cursor.execute("SET foreign_key_checks = 0;")
                cursor.execute("SHOW TABLES")
                tables = list([row[0] for row in cursor])
                for table in tables:
                    print(f"Dropping table: {table}")
                    cursor.execute(f"DROP TABLE {table}")
                cursor.execute("SET foreign_key_checks = 1;")
        for migrations_dir in [settings.BASE_DIR / x / "migrations" for x in self.MIGRATION_DIRS]:
            if not migrations_dir.is_dir():
                continue
            for migration_file in migrations_dir.glob("*.py"):
                if match := re_migration_name.match(migration_file.name):
                    revision = int(match.group(1))
                    if revision > self.PUBLISHED_REVISION:
                        print(f"Deleting migration file: {migration_file}")
                        migration_file.unlink(missing_ok=True)
        self.execute_manage_cmd(["makemigrations", "--noinput"])
        self.execute_manage_cmd(["migrate", "--noinput"])
        print(f"Creating superuser: {settings.BACKEND_TEST_ADMIN_NAME}")
        User.objects.create_superuser(
            username=settings.BACKEND_TEST_ADMIN_NAME,
            password=settings.BACKEND_TEST_ADMIN_PW,
        )
        for name, email, password in settings.BACKEND_TEST_USERS:
            print(f"Creating user: {name}")
            user = User.objects.create_user(name, email=email, password=password)
            print("Create transformer profile for user.")
            TransformerProfile.objects.create(
                profile_name=f'Replace "Value" by {name}',
                transformer_name="regex_edit",
                description="Test transformer created by 'reset_test_db' command.",
                owner=user,
                version=1,
                configuration={
                    "definitions": [
                        {
                            "pattern": "\\bValue\\b",
                            "replacement": "TomlValue",
                            "flag_ascii": False,
                            "flag_ignore_case": False,
                            "flag_multiline": False,
                            "flag_dotall": False,
                            "flag_verbose": False,
                            "_type": "regex_replacement",
                            "_version": 1,
                        }
                    ],
                    "_type": "RegExProfileSettings",
                    "_version": 1,
                },
            )
        for project in settings.BACKEND_TEST_PROJECTS:
            print(f'Creating project: {project["name"]}')
            owner = User.objects.get(username=project["owner"])
            Project.objects.create_project(name=project["name"], description=project["description"], owner=owner)
        print(f"Removing old uploads from directory: {settings.BACKEND_WORKING_DIR}")
        working_dir = Path(settings.BACKEND_WORKING_DIR)
        shutil.rmtree(working_dir / "uploads", ignore_errors=True)
        for path in working_dir.glob("ingest_*"):
            shutil.rmtree(path, ignore_errors=True)
