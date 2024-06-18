#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for MySQL to be ready before continuing
python docker/wait_for_mysql.py

# Apply database migrations
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input --clear

# Add an admin, but only if the database contains no users yet.
if [ -n "${EF_ADMIN_NAME}" ]; then
python manage.py add_admin "${EF_ADMIN_NAME}" "${EF_ADMIN_EMAIL}" --password "${EF_ADMIN_PASSWORD}" -i -s
fi

# Add a user, but only if the database contains no users yet.
if [ -n "${EF_USER_NAME}" ]; then
python manage.py add_user "${EF_USER_NAME}" "${EF_USER_EMAIL}" --password "${EF_USER_PASSWORD}" -i -s
fi

# Run supervisor to start the frontend and backend process.
supervisord -c /etc/supervisor/supervisord.conf
