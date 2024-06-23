.. index::
    !single: Preface

=======
Preface
=======

Welcome to the documentation for *ErbslandFORMER*. This guide is designed to help you understand and utilize the application effectively. The documentation is organized into chapters for users, application administrators, and system administrators. We have minimized redundancies by covering each topic comprehensively in the most relevant chapter, with cross-references provided where necessary.

.. figure:: /images/screenshots/screenshot-project-reviewed.webp
    :width: 80%
    :align: center

    The main project view with transformed and reviewed documents.

.. index::
    single: What is ErbslandFORMER

What is *ErbslandFORMER*?
=========================

If you are not already familiar with *ErbslandFORMER*, it is a tool designed for mass text transformations with the convenience of a web interface. Its target audience includes writers, translators, software documentation authors, academic paper writers, and software developers. The application provides a straightforward workflow, allowing you to import multiple documents into a project and apply text transformations iteratively.

For complex editing tasks, *ErbslandFORMER* allows you to create revisions, enabling you to revert to previous document states and track changes over time. The built-in review system helps you manage completed work and pending reviews, which is particularly useful if you return to a project after some time.

This tool addresses the challenges of text processing using large language models, such as *ChatGPT 4o*. It can automatically process text using these models, capture and apply the output, and handle errors generated during the process. Transformation tasks can process entire books in the background, even if the process takes hours or days.

*ErbslandFORMER* is primarily designed to work with text documents in formats such as Markdown, reStructuredText, XML, JSON, and various programming languages like Python and C++. It is not intended for use with complex document formats from graphical text processors, unless those documents are converted to plaintext or Markdown.

In addition to processing with large language models, the application also supports text transformations using regular expressions. This feature allows you to easily perform tasks such as replacing a protagonist's name in a book or normalizing the spelling of a word across a paper.

.. index::
    single: Chapter Overview

The Chapters in this Documentation
==================================

For a basic overview of the application, start with the :ref:`quick-start` chapter. This chapter provides a concise overview of the project, ideal for those in a hurry. Each section in the quick start chapter links to more detailed parts of the documentation.

If you are ready to set up the application, proceed directly to the :ref:`installation` section. This section contains various guides tailored to different levels of expertise, including a guide for installing the application as a *Docker* container and a detailed step-by-step installation guide for Ubuntu Linux servers.

If the application is already installed and you are a user, start with the :ref:`user manual<user-manual>`. This chapter covers how to work with projects, documents, transformations, and revisions. It provides detailed information about the entire workflow, from importing documents to transforming, reviewing, revising, and exporting the final processed documents.

For system administrators, there is a dedicated :ref:`administrator manual<administrator-manual>`, which offers detailed information on user management and application settings. This chapter explains how to add new users, change user details and passwords, and customize the overall behavior of the application.
