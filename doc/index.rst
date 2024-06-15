
Welcome to ErbslandFORMER documentation!
==========================================

Welcome to *ErbslandFORMER*, a tool designed to efficiently edit and manage large volumes of text through both automated and manual processes. This application was designed for tasks like maintaining software documentation, mass processing code, and correcting and translation of whole books, papers and articles. With its project based architecture, the app is designed to be used by small teams or individuals.

.. figure:: /images/screenshots/screenshot-project-reviewed.webp
    :width: 80%
    :align: center

    The main project view with transformed and reviewed documents.

Text is organized in project, which contain folders and documents. Each document is divided in smaller text fragments, with optimal splitting points based on text format and the chosen text processing tool. The actual edit is facilitated by various specialized tools, ranging from simple regular expressions to advanced large language models like OpenAI's ChatGPT.

Each edit is tracked per fragment, with a review system to keep track on the changes using a detailed diff view. Furthermore, a robust revision system allows you to track changes incrementally, making it easy to revert to previous versions of a project. And, finally, the transformed text can be seamlessly exported and reintegrated into its original source.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    chapters/preface
    chapters/step-by-step-installation
    chapters/sysadmin-installation
    chapters/screenshots

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

