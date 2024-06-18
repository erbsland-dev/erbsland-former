#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import os

from .app_settings import *

# Special Docker Settings File
# -------------------------------------------------------------------------------------------------------------------
# - This file overwrites `ErbslandFormer/settings.py`.
# - Create a copy of /docket/.env.example to /.env and add your secrets there, or use

SECRET_KEY = os.environ.get("EF_SECRET_KEY")
BACKEND_ENCRYPTION_KEY = os.environ.get("EF_BACKEND_ENCRYPTION_KEY")
DEBUG = False
ALLOWED_HOSTS = ["*"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "erbsland_former",
        "USER": "erbsland_former",
        "PASSWORD": os.environ.get("MARIADB_PASSWORD"),
        "HOST": "mariadb",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
        "OPTIONS": {
            "db": "2",
        },
    }
}
STATIC_URL = "static/"
STATIC_ROOT = "/var/www/erbsland-former/static/"
EMAIL_HOST = os.environ.get("EF_EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.environ.get("EF_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EF_EMAIL_HOST_USER", "former@example.com")
EMAIL_HOST_PASSWORD = os.environ.get("EF_EMAIL_HOST_PASSWORD", "***")
EMAIL_SUBJECT_PREFIX = os.environ.get("EF_EMAIL_SUBJECT_PREFIX", "ErbslandFORMER: ")
BACKEND_WORKING_DIR = "/var/www/erbsland-former/working_dir"
TASKS_CELERY_BROKER_URL = "redis://redis/"
TASKS_DATA_REDIS_HOST = "redis"
