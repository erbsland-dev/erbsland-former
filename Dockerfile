# Use the official Python 3.12 slim image as the base image
FROM python:3.12-slim-bookworm AS python_base

# Set the working directory inside the container
WORKDIR /usr/src/app

# Environment variables to prevent Python from writing .pyc files and to buffer output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set an environment variable for Django settings module
ENV DJANGO_SETTINGS_MODULE=ErbslandFormer.settings

# Create a non-root user and group for security purposes
RUN groupadd -r erbsland_former && useradd -r -g erbsland_former erbsland_former

# Update package lists and install necessary packages without recommended extras
# Clean up after installation to reduce the image zie.
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
      build-essential \
      pkg-config \
      python3-dev \
      libmariadb-dev \
      supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a new stage for dependency installation
FROM python_base AS python_deps

# Set the working directory for dependency installation
WORKDIR /app

# Upgrade pip to a specific version
RUN pip install --no-cache-dir --upgrade pip==24.0

# Copy requirements file to the working directory
COPY requirements.txt .

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Install specific versions of additional packages
RUN pip install --no-cache-dir mysqlclient==2.2.4 gunicorn==22.0.0

# Create the final stage for the application
FROM python_deps AS app

# Set the working directory inside the container
WORKDIR /app

# Copy the application code to the working directory
COPY . .

# Overwrite the Django settings with the settings from the docker directory
COPY ./docker/settings.py ./ErbslandFormer/settings.py

# Create the working dir and make it writeable for the app user.
RUN mkdir -p /var/www/erbsland-former/working_dir && \
    chown erbsland_former:erbsland_former /var/www/erbsland-former/working_dir && \
    chmod 700 /var/www/erbsland-former/working_dir

# Copy installed Python packages from the python_deps stage
COPY --from=python_deps /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=python_deps /usr/local/bin/ /usr/local/bin/

# Create the directory for Supervisor logs and make dirs writeable for it.
RUN mkdir -p /var/log/supervisor && \
    chown erbsland_former:erbsland_former /var/log/supervisor && \
    chown erbsland_former:erbsland_former /var/run

# Copy the Supervisor configuration file
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy the entrypoint script and make it executable
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 8000 for the application
EXPOSE 8000

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]