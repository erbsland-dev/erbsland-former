
.. _administrator-manual:
.. index::
    !single: Administration
    single: Administrator Manual

====================
Administrator Manual
====================

This chapter of the manual is designed for administrators of an *ErbslandFORMER* application installation. It covers the different user roles, how to manage users on the system, and highlights a few important settings that affect all users on a server.

User Roles
==========

There are three different user roles in *ErbslandFORMER*: superusers, administrators, and regular users.

.. figure:: /images/user-roles.svg
    :width: 100%

    The three user roles.

A superuser can manage administrator accounts, administrators can manage user accounts, and regular users are limited to using the system. To enforce this separation, superusers and administrators can only manage the system but cannot use it for regular work. This separation is in place to prevent accidents when administrator accounts are used for routine tasks.

Common User Setups
------------------

The number of different user roles required mainly depends on the size and complexity of the installation:

- **Single User**: One user account.
- **Small Team**: One admin account and several user accounts.
- **Company**: One superuser account, one admin per team, and several user accounts.

Each admin requires a regular user account along with their admin account if they intend to perform regular tasks.

Superusers
----------

Typically, there is either none or just a single superuser account on the system. A superuser is also considered a user who has access to the management commands or the configuration on the server. Therefore, if the superuser (e.g., sysadmin) has access to the management commands, they don't need a superuser account in the database.

To create a superuser on the system, use the ``createsuperuser`` management command. Refer to :ref:`admin-how-use-management-cmd` for details on how to use a management command.


.. index::
    !single: User Management
    single: Administration; User Management

User Management
===============

When logging into the application with an *administrator* or *superuser* account, you will be automatically redirected to the user management interface.

.. figure:: /images/screenshots/screenshot-admin-home.webp
    :width: 100%

In this interface, you will see a list of all users registered in the application. If you are logged in as an administrator, you will see both administrators and users. If you are logged in as a superuser, you will also see other superusers.

Each user card displays basic information about the user, such as their username, ID, email address, first and last name. Additionally, you can see when the user last logged into the system and when their account was created.

At the bottom of each row, you will find a button to edit the user details and three vertical dots that reveal a menu with more actions.

.. figure:: /images/screenshots/screenshot-admin-user-popup.webp
    :width: 50%
    :align: center

    The popup that appears when the vertical dots are clicked or hovered over.

.. index::
    single: Permissions
    single: User Management; Permissions

Permissions
-----------

There are a few limitations on what administrators and superusers can do:

- **Administrators**:
    - Can mark user accounts as active and inactive.
    - Can reset user account passwords.
    - Can edit user account details.
    - Cannot see or change superuser accounts.
    - Cannot create new admin accounts or change any details of other admin accounts.
    - Cannot delete user accounts
- **Superusers**:
    - Have no such limitations and can perform all administrative tasks.

.. hint::

    Because superusers have no administrative limitations, it is recommended to only create admin accounts for user management.

.. index::
    single: Add New User
    single: Initial Password
    single: Username
    single: First Name
    single: Last Name
    single: Email Address
    single: User Management; Add New User

Add New User
------------

Clicking the :guilabel:`Add New User` button brings up the interface to add a new user.

.. figure:: /images/screenshots/screenshot-admin-user-add.webp
    :width: 100%

    The user interface to add a new user.

Use this interface to define a :guilabel:`Username`, :guilabel:`First name`, :guilabel:`Last name`, and :guilabel:`Email address` for the user. The :guilabel:`Initial password` field contains a secure randomly generated password that you can send to the new user.

The user is created when you click the :guilabel:`Add New User` button.

.. index::
    single: Add New Admin
    single: User Management; Add New Admin

Add New Admin
-------------

When logged in with a superuser account, there is also a :guilabel:`Add New Admin` button that allows you to add a new admin account. This process is similar to adding a new user, but the created account will have admin permissions.

.. index::
    single: Edit User
    single: First Name
    single: Last Name
    single: Email Address
    single: User Management; Edit User

Edit User
---------

Clicking on the :guilabel:`Edit` button brings up the interface with the user details.

.. figure:: /images/screenshots/screenshot-admin-user-details.webp
    :width: 100%

In this interface, you can edit the user's :guilabel:`First name`, :guilabel:`Last name`, and :guilabel:`Email address`. Clicking :guilabel:`Back` will discard your changes, while clicking :guilabel:`Save and Close` will save your changes.

.. index::
    single: Reset Password
    single: User Management; Reset Password

Reset Password
--------------

Clicking on :guilabel:`Reset Password` allows you to reset the user's password. Enter the new password in both fields in the interface that appears.

.. index::
    single: Make Inactive
    single: User Management; Make Inactive

Make Inactive
-------------

Instead of deleting a user, you should mark them as inactive. Clicking the :guilabel:`Make Inactive` action will mark the user as inactive. An inactive user cannot log into the application.

.. index::
    single: Make Active
    single: User Management; Make Active

Make Active
-----------

The :guilabel:`Make Active` button appears for inactive users. Clicking it will reactivate the user, allowing them to log into the application again.

.. index::
    single: Delete User
    single: User Management; Delete User

Delete User
-----------

Only superusers can delete users. However, it is generally not recommended to delete users who have already performed tasks in the application. Instead, mark the user as inactive. The delete user action is available for cases where a user or administrator was accidentally created and has not yet been used.

.. warning::

    Deleting users who have actively worked with the application may cause various side effects and is not recommended.


.. _admin-how-use-management-cmd:
.. index::
    !single: Management Commands
    single: Management Commands; How to Use
    single: Administration; Management Command

How to Use the Management Commands
==================================

The management commands are an alternative for system administrators to perform administrative tasks on the command line. To use the management commands for the server, you need to be logged in as the same user under which the application is running. If a system administrator set up the server for you, ask them to run the management commands or create a limited login for you to execute these commands.

Regular Server
--------------

After logging into a regular server as an administrator, you can run management commands as follows:

.. code-block:: console

    test@erbsland-former:~$ sudo su erbsland_former
    erbsland_former@erbsland-former:/home/test$ cd /var/www/erbsland-former
    erbsland_former@erbsland-former:/var/www/erbsland-former$ source venv/bin/activate
    (venv) erbsland_former@erbsland-former:/var/www/erbsland-former$ python app/manage.py add_user test1
    (...)
    (venv) erbsland_former@erbsland-former:/var/www/erbsland-former$ █

Docker
------

After logging into the Docker management server, you can run management commands as follows:

.. code-block:: console

    test@erbsland-former:~$ docker exec -it erbsland-former-app python manage.py add_user test1
    (...)
    test@erbsland-former:~$ █

.. index::
    single: Management Commands; Useful
    single: Useful Management Commands

Useful Management Commands
--------------------------

Here are several useful commands for administering the server:

- **changepassword**: Use this command to change a user's password.
- **add_user**: Use this command to add a new regular user to the application.
- **add_admin**: Use this command to add a new administrator to the application.
- **createsuperuser**: Use this command to create a superuser for the application.
- **list_extensions**: Use this command to get a list of all activated extensions.

Use the command line argument ``--help`` with any of these commands to get additional usage information.

.. index::
    single: Global Settings
    single: Important Global Settings

Important Application-Wide Settings
===================================

The application provides several settings that can only be configured on the server. These settings affect all users and allow you to customize, extend, or limit the application's capabilities.

.. note::

    If you are unfamiliar with server administration, please ask your system administrator to set up these options for you.

How to Change Global Settings
-----------------------------

In the server setup, you created a new settings file named `my_settings.py`. To modify global settings, simply add the variable at the end of this file to overwrite its default value.

.. index::
    single: Document Syntax
    single: Size Unit

Preselect a Default Document Syntax or Size Unit
------------------------------------------------

You can preselect the default document syntax and size unit displayed in the user interface if a user does not have a preference for a task. Set the defaults using the settings :ref:`setting-backend_default_syntax_handler` and :ref:`setting-backend_default_size_calculator`. Specify the correct *identifier* for the syntax handler or size calculator. Use the management command `list_extensions` to get a list of all identifiers.

Disabling a Document Syntax, Transformer, or Size Unit
------------------------------------------------------

If you want to hide a certain document syntax, transformer, or size unit, use the settings :ref:`setting-backend_ignore_syntax_handler`, :ref:`setting-backend_ignore_size_calculator`, and :ref:`setting-backend_transformer`.

Limiting the Upload Size
------------------------

To limit the size of uploaded files, change the settings :ref:`setting-backend_ingest_upload_file_size`, :ref:`setting-backend_ingest_document_size`, or :ref:`setting-backend_ingest_file_count`.

AI Transformer Application Settings
===================================

The AI transformer can be configured to require, allow, or disallow personal API keys for its processing.

Set an Application-Wide API Key
-------------------------------

Use the settings :ref:`setting-ai_api_key`, :ref:`setting-ai_organization_id`, and :ref:`setting-ai_project_id` to set an application-wide API key for the AI transformer profiles. When set at the application level, the key is never exposed to the users.

If there is no application-wide setting, each user must provide their own API key for the transformer. An individual key per user allows you to track individual usage but also means that the key is exposed to the user.

By default, users are allowed to overwrite the application-wide key with a custom one. If you want to enforce the application-wide key, set :ref:`setting-ai_allow_user_overrides` to `False`.

Limit the Allowed Language Models
---------------------------------

By configuring a custom list of identifiers with the :ref:`setting-ai_allowed_models`, you can limit the language models a user can select and use.

