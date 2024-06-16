.. _architecture:
.. index::
    !single: Architecture

============
Architecture
============

System Architecture
===================

The system architecture is divided into a frontend and a backend, designed for scalability and ease of maintenance.

.. figure:: /images/architecture-overview.svg
    :width: 100%

Frontend
--------

The frontend is served via *WSGI*, using either *Apache* or *nginx* as the web server. The application is built on the *Django framework*, which provides database abstraction and modularity, making the system easy to maintain and extend.

*Redis* is used for communication with the backend to start background tasks and receive real-time updates on their progress and status. For enhanced performance, *Django* is configured to use *Redis* as a web cache.

Backend
-------

The backend uses *Celery* as a distributed task scheduler, allowing tasks to run in the background over extended periods. Like the frontend, the backend is based on the *Django framework*, leveraging its database abstraction to access data. Background tasks also report status and logs via *Redis* to be displayed in the frontend.

Connection Layer
----------------

The frontend and backend are connected via a single instance of *Redis* and a database such as *MariaDB*, *MySQL*, or *Postgres*.

Scalability
-----------

This architecture supports a single server setup, where the frontend, backend, and database run on one server. It also offers the flexibility to scale by adding multiple frontend and backend instances as needed.


Software Architecture
=====================

The software architecture leverages *Django's* modular application system to separate the individual components of the software, ensuring modularity and extensibility.

.. figure:: /images/software-architecture.svg
    :width: 100%

Main Goals
----------

Different users and companies have varying requirements for large-scale text processing. Therefore, the primary goal of the chosen architecture is to create a system that is both modular and extensible. This design allows users to utilize the powerful built-in transformation tools and easily develop their own custom tools. Since these extensions are written as separate "Django Apps," they seamlessly integrate into the system and can be distributed in separate repositories for straightforward deployments.

Extension Points
----------------

The current architecture supports the following extension points:

- **Transformation modules**: Process text fragments.
- **Size calculators**: Provide a size unit to determine the best splitting points in documents.
- **Syntax handlers**: Understand document syntax and return a document structure and metadata to split the document into fragments.

Core Modules
------------

Backend Module
~~~~~~~~~~~~~~

The backend module is the largest component of the application. It includes all database models, the actions that run in the background, and the base interfaces for the transformer, size calculator, and syntax handler interfaces. It also contains management tools and shared utilities used throughout the application.

Design Module
~~~~~~~~~~~~~

The design module contains everything related to styling and building the user interface, without any application logic. It is composed of multiple Django Apps for easier maintenance and portability. This module includes all HTML, CSS, and JavaScript required for the interactive user interface.

Editor Module
~~~~~~~~~~~~~

The editor module implements the user interface logic, building on top of the backend and design modules. The separation line between the design and editor modules is that the design module provides the overall design and base views, while the editor module combines the actual user interface with the application logic. This separation allows the overall style of the application to be changed by updating the design module, with minimal changes required in the editor module.

Tasks Module
~~~~~~~~~~~~

The tasks module provides a framework and interface to *Redis* and *Celery*. It implements a simple task system that allows tasks to be executed as background processes and their progress to be monitored. Additionally, it provides an action framework that enables easy registration and implementation of individual actions run as tasks.

Extensions
----------

Currently, there are two built-in extensions for the application:

Regular Expression Transformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This extension allows text to be transformed using one or more regular expression patterns.

AI Transformer
~~~~~~~~~~~~~~

The AI transformer uses OpenAI's ChatGPT API to transform text using natural language prompts and output matching. This extension also includes special size calculators for the tokens of various language models, enabling text to be split into optimal chunk sizes for the selected model.
