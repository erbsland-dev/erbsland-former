
.. _user-manual:
.. index::
    !single: User Manual

===========
User Manual
===========

Log In
======

To start using *ErbslandFORMER*, you need to log in to your account. Follow the steps below to access the application.

**Open the Application**: Enter the URL of your *ErbslandFORMER* server in your web browser. You will see the welcome screen. Click the green :guilabel:`Log in` button to proceed to the login page.

.. figure:: /images/screenshots/screenshot-user-welcome.webp
    :width: 100%

    The *ErbslandFORMER* welcome screen.

**Enter Credentials**: On the login page, enter your username and password. After entering your credentials, click the green :guilabel:`Log in` button.

.. figure:: /images/screenshots/screenshot-user-login.webp
    :width: 100%

    The login page prompts you to enter your username and password.

Once logged in, you will be redirected to the home page of the application where you see your current projects.

.. hint::

    If you have forgotten your password or username, click the "Forgotten your password or username?" link below the login form to recover your account.

Make sure to use the credentials provided by your system administrator. If you experience any issues logging in, please contact your system administrator for assistance.


.. index::
    single: Create a New Project
    single: User Manual; Create a New Project

Create a New Project
====================

To start working with *ErbslandFORMER*, you need to create a new project. Follow the steps below to create and configure your project.

If there are no projects are available, you will see an empty project list as shown below.

.. figure:: /images/screenshots/screenshot-user-empty-project-list.webp
    :width: 100%

    The Projects page with an empty project list.

**Add a New Project**: Click the green :guilabel:`Add New Project` button to create a new project. This will open the "Add New Project" form.

.. figure:: /images/screenshots/screenshot-user-add-new-project.webp
    :width: 100%

    The "Add New Project" form.

**Fill in Project Details**: In the form, enter the project details:

- :guilabel:`Project Name`: Provide a unique and concise name for your project. For example, "Erbsland Qt TOML".
- :guilabel:`Brief Description`: Optionally, add a brief description of the project. This can be helpful if you work in a team.
- :guilabel:`Primary Document Syntax`: Select the primary syntax to be used for the documents in this project. For example, "reStructuredText".

After filling in the details, click the green :guilabel:`Create Project` button.

**View the New Project**: After creating the project, you will be redirected to the new project's page. Here, you can start importing documents and managing your project.

.. figure:: /images/screenshots/screenshot-user-empty-project.webp
    :width: 100%

    The newly created project page.

With the project created, you can now proceed to import documents and begin working with *ErbslandFORMER*.


.. index::
    single: Importing Files
    single: User Manual; Importing Files

Importing Files
===============

To import initial or additional documents into your project, click the green :guilabel:`Import Documents` button when the project is empty, or select :guilabel:`Import Documents` from the :guilabel:`Project Actions` menu.

.. note::

    You can only import new documents into the latest revision of a project.

After clicking the :guilabel:`Import Documents` button or menu entry, the import assistant will be displayed.

.. figure:: /images/screenshots/screenshot-user-import-upload-file.webp
    :width: 100%

    The first page of the import assistant.

Select either a single text document or a ZIP archive containing multiple documents, then click the green :guilabel:`Upload File` button to start the analysis of the selected file.

.. figure:: /images/screenshots/screenshot-user-import-analyze-files.webp
    :width: 100%

    The progress view while the upload is analyzed.

The Import Setup
----------------

After the analysis is complete, the setup page will display a list of all suitable documents for import.

.. figure:: /images/screenshots/screenshot-user-import-setup.webp
    :width: 100%

    The import setup with the list of documents from the upload.

Configuring Size Unit and Range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the setup page, configure the size unit you want to use for splitting the documents into fragments. When you select a new unit from the :guilabel:`Unit for Size` dropdown, the :guilabel:`Fragment Range` below will update with the recommended range.

The size unit should match the transformation method you intend to use, allowing the splitting algorithm to choose optimal fragment sizes. For example, if you plan to transform the text using the *GPT-4o language model*, select "Tokens for GPT-4o" with the recommended range.

- :guilabel:`Minimum Size`: The minimum size a fragment should be. Depending on the situation, the splitter may need to create smaller fragments.
- :guilabel:`Maximum Size`: The maximum size of a fragment. If the splitter cannot keep fragments smaller or equal to this size, the splitting process will stop with an error.

Document List Overview
~~~~~~~~~~~~~~~~~~~~~~

The document list shows all documents found in your import. Here are the columns you'll see:

- :guilabel:`Name`: The name of the document in your project. You can edit this to simplify or shorten names, but remember that these names will also be used for export.
- :guilabel:`Folder`: The folder where the document will be stored in your project. This can also be edited.
- :guilabel:`Document Syntax`: The detected document syntax. Choosing the correct syntax is crucial, as the splitting algorithm depends on it. For example, the algorithm for Markdown files differs from that for Python source code.
- :guilabel:`Planned Action`: Indicates whether the document will be added to the project (:guilabel:`Add`) or ignored (:guilabel:`Ignore`).

Click the green :guilabel:`Generate Preview` button at the end of the document list to proceed with the assistant.

The Import Preview
------------------

*More documentation is coming soon*
