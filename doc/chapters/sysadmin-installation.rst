
.. _sysadmin-installation:

======================================
Installation for System Administrators
======================================

This guide provides a concise overview of how to install *ErbslandFORMER* for system administrators. It focuses on the key elements without detailing the execution of each task. For a more detailed guide, refer to the :ref:`step-by-step-installation`.

Requirements
============

- **Python 3.12+**

  The application requires Python 3.12 or newer and the packages listed in `requirements.txt` or `requirements.in`.

- **Apache or nginx: Web Server to Run a WSGI Application**

  A web server or proxy, like Apache or nginx, is required to run the frontend application.

- **Redis: Message Broker for Celery and the Frontend**

  Redis is necessary as a message broker for Celery to handle background tasks.

- **MariaDB/MySQL/PostgreSQL Database**

  A database such as MySQL, MariaDB, or PostgreSQL is needed to store all application data.

- **MySQL Database Client for Python**

  A MySQL database client for Python, such as ``mysqlclient``, is required. This client is not part of the ``requirements.txt`` and should be installed from the distribution.

Application User
================

Create a system user for the application, e.g., ``erbsland_former``, with a group and a shell. A home directory is not required.

Application Directory Structure
===============================

Preferably in ``/var/www/erbsland-former``, create the following directory structure:

.. code-block:: plain

    ├───◆ /var/www/erbsland-former
        ├───◆ app            # Application files / Configuration (via git clone)
        ├───◆ static         # Static files served by the web server.
        ├───◆ venv           # Python virtual environment.
        ├───◆ working_dir    # Directory for temporary files.

    drwxr-xr-x | erbsland_former erbsland_former | app/
    drwxr-xr-x | erbsland_former erbsland_former | static/
    drwxr-xr-x | erbsland_former erbsland_former | venv/
    drwx------ | erbsland_former erbsland_former | working_dir/

Create the directories and set the appropriate permissions:

.. code-block:: console

    test@erbsland-former:~$ sudo mkdir /var/www/erbsland-former
    test@erbsland-former:~$ sudo chown erbsland_former:erbsland_former /var/www/erbsland-former
    test@erbsland-former:~$ sudo chmod 755 /var/www/erbsland-former
    test@erbsland-former:~$ sudo mkdir /var/www/erbsland-former/static
    test@erbsland-former:~$ sudo chown erbsland_former:erbsland_former /var/www/erbsland-former/static
    test@erbsland-former:~$ sudo chmod 755 /var/www/erbsland-former/static
    test@erbsland-former:~$ sudo mkdir /var/www/erbsland-former/working_dir
    test@erbsland-former:~$ sudo chown erbsland_former:erbsland_former /var/www/erbsland-former/working_dir
    test@erbsland-former:~$ sudo chmod 700 /var/www/erbsland-former/working_dir

Clone the application repository and set up the virtual environment:

.. code-block:: console

    test@erbsland-former:~$ sudo su erbsland_former
    erbsland_former@erbsland-former:/home/test$ cd /var/www/erbsland-former
    erbsland_former@erbsland-former:/var/www/erbsland-former$ git clone https://github.com/erbsland-dev/erbsland-former.git app
    erbsland_former@erbsland-former:/var/www/erbsland-former$ python3 -m venv --system-site-packages venv
    erbsland_former@erbsland-former:/var/www/erbsland-former$ source venv/bin/activate
    (venv) erbsland_former@erbsland-former:/var/www/erbsland-former$ pip install -r app/requirements.txt

Setup Redis and MariaDB
=======================

Activate Redis:

.. code-block:: console

    test@erbsland-former:~$ sudo systemctl enable redis-server
    test@erbsland-former:~$ sudo systemctl start redis-server
    test@erbsland-former:~$

Set up MySQL:

.. code-block:: console

    test@erbsland-former:~$ sudo systemctl enable mariadb
    test@erbsland-former:~$ sudo systemctl start mariadb
    test@erbsland-former:~$ sudo mariadb
    MariaDB [(none)]> CREATE DATABASE erbsland_former CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    MariaDB [(none)]> CREATE USER erbsland_former@localhost IDENTIFIED BY '[random password]';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON erbsland_former.* TO erbsland_former@localhost;
    MariaDB [(none)]> FLUSH PRIVILEGES;

System Setup
============

Copy the file ``settings.py`` in the application directory ``ErbslandFormer`` and rename it to ``my_settings.py``. Update ``wsgi.py`` with the name of your settings file.

Update your ``my_settings.py`` file:

- Set a random ``SECRET_KEY``.
- Set a random ``BACKEND_ENCRYPTION_KEY``.
- Set the database host, name, user, and password.
- Set the ``STATIC_ROOT`` to the ``static`` directory.
- Set the ``BACKEND_WORKING_DIR`` to the ``working_dir`` directory.
- Configure all ``EMAIL_...`` settings to enable email functionality.
- Remove the last section enclosed in ``[remove]``.

Run a check, collect all static files, and initialize the database. Ensure you set the environment variable ``DJANGO_SETTINGS_MODULE`` to your settings file.

.. code-block:: console

    $ export DJANGO_SETTINGS_MODULE=ErbslandFormer.my_settings
    $ python app/manage.py check
    System check identified no issues (0 silenced).
    $ python app/manage.py collectstatic
    189 static files copied to '/var/www/erbsland-former/static'.
    $ python app/manage.py migrate

Create a superuser and regular users for the system:

.. code-block:: console

    $ python app/manage.py createsuperuser --username ef_admin --email ef_admin@example.com
    $ python app/manage.py add_user user1 user1@example.com
    $ python app/manage.py add_user user2 user2@example.com
    $ python app/manage.py add_user user3 user3@example.com

Setup the Backend Process
=========================

Set up *Celery* as a background process. Use the ``erbsland-former.service`` template for this setup.

.. code-block:: console

    test@erbsland-former:~$ sudo cp /var/www/erbsland-former/app/ErbslandFormer/erbsland-former.service /etc/systemd/system/
    test@erbsland-former:~$ sudo chown root:root /etc/systemd/system/erbsland-former.service
    test@erbsland-former:~$ sudo chmod 644 /etc/systemd/system/erbsland-former.service
    test@erbsland-former:~$ sudo nano /etc/systemd/system/erbsland-former.service
    test@erbsland-former:~$ sudo systemctl enable erbsland-former
    test@erbsland-former:~$ sudo systemctl start erbsland-former

Ensure the service is started successfully by checking the logs with ``journalctl -r``.

Example service file:

.. code-block:: ini
    :linenos:
    :emphasize-lines: 7-12

    [Unit]
    Description=ErbslandFORMER Celery Service
    After=network.target

    [Service]
    Type=simple
    User=erbsland_former
    Group=erbsland_former
    WorkingDirectory=/var/www/erbsland-former/app/
    Environment="DJANGO_SETTINGS_MODULE=ErbslandFormer.my_settings"
    ExecStart=/usr/bin/env bash -c 'source /var/www/erbsland-former/venv/bin/activate && exec python3 -m celery -A tasks.celery_app worker --loglevel=info'
    ExecStop=/usr/bin/env bash -c 'source /var/www/erbsland-former/venv/bin/activate && exec python3 -m celery -A tasks.celery_app control shutdown'
    Restart=always

    [Install]
    WantedBy=multi-user.target

Configure Apache
================

You will find an example Apache configuration file named ``apache.conf`` in the ``ErbslandFormer`` directory. Copy this file to the Apache configuration directory and enable the site. Adjust all paths and names according to your setup.

.. code-block:: console

    test@erbsland-former:~$ sudo cp /var/www/erbsland-former/app/ErbslandFormer/apache.conf /etc/apache2/sites-available/former.erbsland.com.conf
    test@erbsland-former:~$ sudo a2ensite former.erbsland.com.conf

Below is an example of the Apache configuration. Ensure you modify the paths and user names as needed for your setup.

.. code-block:: apache

    <VirtualHost *:80>
        ServerName former.erbsland.com
        DocumentRoot /var/www/html
        ErrorLog ${APACHE_LOG_DIR}/former.erbsland.com_error.log
        CustomLog ${APACHE_LOG_DIR}/former.erbsland.com_access.log combined
        RewriteEngine On
        RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
    </VirtualHost>
    <VirtualHost *:443>
        ServerName former.erbsland.com
        DocumentRoot /var/www/html
        Alias /static/ /var/www/erbsland-former/static/

        # WSGI
        WSGIDaemonProcess former.erbsland.com \
            home=/var/www/erbsland-former/ \
            python-home=/var/www/erbsland-former/venv \
            python-path=/var/www/erbsland-former/app:/var/www/erbsland-former/venv/lib/python3.12/site-packages \
            user=erbsland_former
        WSGIProcessGroup former.erbsland.com
        WSGIScriptAlias / /var/www/erbsland-former/app/ErbslandFormer/wsgi.py
        <Directory /var/www/erbsland-former/app>
            <Files wsgi.py>
                Require all granted
            </Files>
        </Directory>
        <Directory /var/www/erbsland-former/static>
            Require all granted
        </Directory>

        # SSL Configuration
        SSLEngine on
        SSLCertificateFile /etc/ssl/certs/former.erbsland.com.pem
        SSLCertificateKeyFile /etc/ssl/private/former.erbsland.com.pem
        SSLCertificateChainFile /etc/ssl/certs/former.erbsland.com_chain.pem

        # Security Enhancements
        SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
        SSLCipherSuite HIGH:!aNULL:!MD5:!3DES:!CAMELLIA:!DES:!eNULL
        SSLHonorCipherOrder on
        SSLCompression off
        SSLSessionTickets off

        # HSTS (HTTP Strict Transport Security)
        Header always set Strict-Transport-Security "max-age=63072000; includeSubdomains; preload"

        # OCSP Stapling
        SSLUseStapling on
        SSLStaplingResponderTimeout 5
        SSLStaplingReturnResponderErrors off
        SSLStaplingCache shmcb:/var/run/ocsp(128000)

        # Logging
        ErrorLog ${APACHE_LOG_DIR}/former.erbsland.com_error.log
        CustomLog ${APACHE_LOG_DIR}/former.erbsland.com_access.log combined
    </VirtualHost>

Ensure you adapt this example configuration to comply with the SSL standards of your company. Restart the web server to activate the new configuration.

.. code-block:: console

    test@erbsland-former:~$ sudo systemctl restart apache2

Done
====

This is the basic setup for a single host installation of the application. The application can easily scale across multiple frontend and backend instances, using *Redis* and *Celery* to distribute the workload.
