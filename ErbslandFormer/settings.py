#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import sys
from pathlib import Path

from .app_settings import *

# README - Settings Template
# -------------------------------------------------------------------------------------------------------------------
# This template assists in setting up the application.
# Do not use as-is for production; it's configured for development purposes.
# -------------------------------------------------------------------------------------------------------------------
# All configurations in `app_settings.py` are essential for proper functionality and should remain unchanged.
# -------------------------------------------------------------------------------------------------------------------
# Individual applications within this project have `settings.py` files. You can override their local settings by
# defining variables in the main settings file.
# -------------------------------------------------------------------------------------------------------------------
# Refer to the Django Documentation for guidance on secure setup.


# Create a random secret key for your application.
# Use the following command to generate a suitable secret key:
# ```
# python -c "import secrets; print(secrets.token_urlsafe(64))"
# ```
SECRET_KEY = "django-insecure-*2k$#0$30=80%oaa_hf)=tfatkqzg&sjgr=q8aa-%@)%*4!(1^"

# Create a random secret key that is used to encrypt/decrypt passwords and keys in the user settings.
# Changing this key will render all sensitive settings useless and require that the user needs to enter
# credentials and API keys again. See also `BACKEND_ENCRYPTION_KEY_FALLBACKS` for a way to rotate
# the encryption key.
BACKEND_ENCRYPTION_KEY = "backend-insecure-DuJcyCCAEXtelpSUCIwYlQCZaZ3Xfwfo4Le3bTas1w8"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Limit your instance to hosts in your local network.
ALLOWED_HOSTS = ["localhost"]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "erbsland_former",
            "USER": "erbsland_former",
            "PASSWORD": "***",
            "HOST": "localhost",
            "OPTIONS": {
                "charset": "utf8mb4",
            },
        }
    }

# Use the Redis Server also as a cache.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "db": "2",
        },
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "static/"

# Email settings, required for password reset.
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend
EMAIL_HOST = "smtp.example.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "former@example.com"
EMAIL_HOST_PASSWORD = "******"
EMAIL_SUBJECT_PREFIX = "ErbslandFORMER: "

# [remove]
# Remove these lines from your local settings file
raise ValueError("\n" + "!" * 78 + "\n!!!\n!!!   Do not use the settings template!\n!!!\n" + "!" * 78)
# [/remove]
