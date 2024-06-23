
.. _requirements:
.. index::
    !single: Requirements

============
Requirements
============

This application consists of a frontend, a database, a communication layer and a backend that executes tasks in separate threads. The following are required:

.. index::
    single: Python
    single: Requirements; Python

Python 3.12
===========

The application is written for Python 3.12 or newer and requires the packages listed in :file:`requirements.txt` or file:`requirements.in`. While the listed versions are tested, you may update them to the latest versions if needed.

Updates beyond the versions in :file:`requirements.txt`
-------------------------------------------------------

While the application is tested with Python 3.12, it should also work with later versions of Python. If you are running this application as a *WSGI* module, the WSGI extension of the webserver had to be built for the Python version you are using for the application.

This application is based on the extensive `Django Web Framework <https://www.djangoproject.com>`_. We use the latest major version 5 of Django as basis for *ErbslandFORMER*. As this project carefully maintains backward compatibility in the same major version of the framework, this application should run on any later version of the Django framework with the same major version.

.. index::
    single: Webserver
    single: Requirements; Webserver

Webserver or Proxy to run a WSGI application
============================================

A web server or proxy, like *Apache*, *nginx* or *gunicorn*, is required to run the frontend application. Refer to chapter :ref:`installation`, where various setups are described. For testing purposes, you can use *Django's* built-in web server.

We recommend to run the application using the *Apache webserver* with the WSGI extension module, as described in the installation manual. This setup provides the most flexibility and allows you run and integrate more services on the same server.

.. index::
    single: Redis
    single: Requirements; Redis

Redis: Message Broker for Celery and the Frontend
=================================================

*Redis* is necessary as a message broker for the *Celery* task scheduler to handle background tasks that may take time to complete. *Redis* also facilitates communication between running tasks and the web interface to display progress and logs.

The application also uses the same *Redis* server to cache the rendering of the websites. The used *Redis* instances and connections can be configured individually.

.. index::
    single: Database
    single: Requirements; Database

MariaDB/MySQL/Postgres Database
===============================

A database like MySQL, MariaDB, or Postgres is needed to store all processed data. For handling large amounts of data, ensure your database installation is appropriately scaled.

We recommend and also tested the application with MariaDB.