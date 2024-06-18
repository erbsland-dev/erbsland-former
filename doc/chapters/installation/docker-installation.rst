.. _docker-installation:
.. index::
    single: Installation; Docker

=======================
Installation via Docker
=======================

The application repository contains all the necessary configuration files for a fast and easy setup using Docker. This guide assumes that you are running these commands on a server with Docker support installed. If Docker is not installed, please refer to the `Docker documentation <https://docs.docker.com>`_ for installation instructions.

Clone the Repository
====================

Clone the *ErbslandFORMER* repository from GitHub into a subdirectory in your home directory. The following command will create a subdirectory named ``erbsland-former`` with the application files.

.. code-block:: console

    test@erbsland-former:~$ git clone https://github.com/erbsland-dev/erbsland-former.git
    (...)
    test@erbsland-former:~$ █

Prepare the Configuration
=========================

Create a copy of the ``.env.example`` file from the ``docker`` subdirectory. Copy this file as ``.env`` in the project root directory.

.. code-block:: console

    test@erbsland-former:~$ cp erbsland-former/docker/.env.example erbsland-former/.env
    test@erbsland-former:~$ █

Edit the ``.env`` file to configure your environment settings.

.. code-block:: console

    test@erbsland-former:~$ nano erbsland-former/.env
    (...)
    test@erbsland-former:~$ █

The copied ``.env`` file should look like this:

.. code-block:: toml

    EF_SECRET_KEY="[random secret key 32+ characters!]"
    EF_BACKEND_ENCRYPTION_KEY="[random encryption key 32+ characters!]"
    EF_EMAIL_HOST="smtp.example.com"
    EF_EMAIL_PORT="587"
    EF_EMAIL_HOST_USER="former@example.com"
    EF_EMAIL_HOST_PASSWORD="[SMTP Password]"
    EF_EMAIL_SUBJECT_PREFIX="ErbslandFORMER: "
    EF_ADMIN_NAME="admin"
    EF_ADMIN_EMAIL="admin@example.com"
    EF_ADMIN_PASSWORD="[random admin password, 16+ characters]"
    EF_USER_NAME="user"
    EF_USER_EMAIL="user@example.com"
    EF_USER_PASSWORD="[random user password, 16+ characters]"
    MARIADB_PASSWORD="[random db password]"
    MARIADB_ROOT_PASSWORD="[random db root password]"

Secrets
-------

The secrets are random keys used for signing and encrypting data. If these keys change, the application will no longer have access to the encrypted data in the database. Make sure you keep a backup of these keys along with your database backup.

.. _docker-ef-secret-key:

``EF_SECRET_KEY``
~~~~~~~~~~~~~~~~~

This configures the secret key used to encrypt and sign local session data. Generate a random key with at least 32 characters. Use the following Python command to generate such a key.

.. code-block:: console

    test@erbsland-former:~$ python3 -c "import secrets; print(secrets.token_urlsafe(32));"
    Ca8YJlXQfyxoYhhqwOE6sPXRa2lDT4yOyX1RDmlIh8s
    test@erbsland-former:~$ █

Copy the generated key (e.g., ``Ca8YJlXQfyxoYhhqwOE6sPXRa2lDT4yOyX1RDmlIh8s``) into the ``.env`` file as shown below:

.. code-block:: toml

    EF_SECRET_KEY="Ca8YJlXQfyxoYhhqwOE6sPXRa2lDT4yOyX1RDmlIh8s"

``EF_BACKEND_ENCRYPTION_KEY``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This line configures the secret key used to encrypt passwords and keys in the user settings. Create a new random key as shown in :ref:`docker-ef-secret-key`.

Email Server
------------

To enable password resets, the server needs to be able to send emails. Create a dedicated email account on your email server and configure the connection details here.

``EF_EMAIL_HOST``
~~~~~~~~~~~~~~~~~

Set this value to the hostname or IP address of your email server.

``EF_EMAIL_PORT``
~~~~~~~~~~~~~~~~~

This is the port used to connect to the email server. The port number also defines the protocol used for the connection.

``EF_EMAIL_HOST_USER``
~~~~~~~~~~~~~~~~~~~~~~

Specify the email account used to send emails.

``EF_EMAIL_HOST_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify the password for this email account.

``EF_EMAIL_SUBJECT_PREFIX``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this value to specify a prefix that will be added to the subject of all emails sent from the application.

Initial Admin and User Creation
-------------------------------

The Docker configuration will automatically create an administrator and user account when the database is initially set up. Specify the details for these initial accounts with the following values. After deploying the Docker image, you can change the passwords in the user interface of the application and manage users with the created admin account.

These values are ignored after the initial deployment.

``EF_ADMIN_NAME``, ``EF_ADMIN_EMAIL``, ``EF_ADMIN_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify the name, email address, and password of the administrator user.

.. hint::

    Please create a secure random password using the method shown in section :ref:`docker-ef-secret-key`.

``EF_USER_NAME``, ``EF_USER_EMAIL``, ``EF_USER_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify the name, email address, and password of the initial user.

.. hint::

    Please create a secure random password using the method shown in section :ref:`docker-ef-secret-key`.

Database Configuration
----------------------

Even though the database is encapsulated in a Docker container, you must create random passwords for the application database user and the root user of the database server.

``MARIADB_PASSWORD``, ``MARIADB_ROOT_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate a random password using the method shown in section :ref:`docker-ef-secret-key`.

Example
-------

A properly configured ``.env`` file might look like this:

.. code-block:: toml

    EF_SECRET_KEY="jFRaiEUYu1B62uc9CJvBPDtVS-s5LNkPA7xGtllKa6E"
    EF_BACKEND_ENCRYPTION_KEY="38QsDfptECO3uAD61jAPgNEHBoRGlA8Q2kZTZY9IouI"
    EF_EMAIL_HOST="smtp.your-company.com"
    EF_EMAIL_PORT="587"
    EF_EMAIL_HOST_USER="former@your-company.com"
    EF_EMAIL_HOST_PASSWORD="DTUjrEGD-I67g0f4dVCQaC"
    EF_EMAIL_SUBJECT_PREFIX="ErbslandFORMER: "
    EF_ADMIN_NAME="admin"
    EF_ADMIN_EMAIL="erbsland-former-admin@your-company.com"
    EF_ADMIN_PASSWORD="NbSO7pu_l79d2XxFZytcGg"
    EF_USER_NAME="joe.smith"
    EF_USER_EMAIL="joe.smith@your-company.com"
    EF_USER_PASSWORD="OnLMDtOAKxTvy96JQmXR4Q"
    MARIADB_PASSWORD="AZOEkG13BJ8lGme05dNMPHWBWZF9ZqTV3FWPLcrXjuM"
    MARIADB_ROOT_PASSWORD="HD6RfV58nE5GM4vdOVzlBc0MP07ppqXYDe45qiz3A-E"

Build the Docker Image
======================

To build the Docker image with your configuration, change to the `erbsland-former` directory and run `docker compose build app`. This command will build the Docker image used for deployment.

.. code-block:: console

    test@erbsland-former:~$ cd erbsland-former
    test@erbsland-former:~/erbsland-former$ docker compose build app
    (...)
    test@erbsland-former:~/erbsland-former$ █

Start the Docker Container
==========================

After successfully building the Docker image, start the container with the command `docker compose up -d`. The `-d` option will start the container in detached mode. If you encounter any problems, start it without the `-d` option to see log messages.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker compose up -d
    [+] Running 5/5
     ✔ Network erbsland-former_default    Created
     ✔ Container erbsland-former-mariadb  Started
     ✔ Container erbsland-former-redis    Started
     ✔ Container erbsland-former-app      Started
     ✔ Container erbsland-former-nginx    Started
    test@erbsland-former:~/erbsland-former$ █

Accessing the Application
=========================

Once the Docker containers are up and running, you can access the application by visiting ``http://[your server]:8080`` in your web browser. Ensure that the necessary ports are open and accessible.

Monitoring and Logs
===================

To monitor the logs of your running Docker containers, you can use the ``docker logs`` command. This can be particularly useful for debugging issues.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker logs -f erbsland-former-app

To view logs for all services, use:

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker compose logs -f

Updating the Application
========================

To update the application, follow these steps:

1. Pull the latest changes from the repository.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ git pull origin main

2. Rebuild the Docker image.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker compose build app

3. Restart the Docker containers.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker compose up -d

Backing Up Data
===============

Ensure that you have a backup strategy for your database and configuration files. Regular backups can prevent data loss in case of failure.

To back up the database, you can use the ``mysqldump`` command within the MariaDB container.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker exec erbsland-former-mariadb mysqldump -u root -p[ROOT_PASSWORD] erbsland_former > backup.sql

Security Considerations
=======================

- **Firewall**: Make sure the server is not accessible from the internet and ensure that only necessary ports are open.
- **SSL/TLS**: Use SSL/TLS to encrypt data in transit. Configure your web server (nginx) to use a valid SSL certificate.
- **Environment Variables**: Keep your `.env` file secure and create backup from it. Do not expose sensitive information.

Troubleshooting
===============

If you encounter issues, consider the following steps:

1. Check container status.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker ps

2. Inspect logs for errors.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker logs -f erbsland-former-app

3. Restart individual containers if needed.

.. code-block:: console

    test@erbsland-former:~/erbsland-former$ docker compose restart erbsland-former-app
