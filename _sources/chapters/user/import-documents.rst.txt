

.. index::
    pair: Import; Document
    single: User Manual; Import Documents

================
Import Documents
================

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
================

After the analysis is complete, the setup page will display a list of all suitable documents for import.

.. figure:: /images/screenshots/screenshot-user-import-setup.webp
    :width: 100%

    The import setup with the list of documents from the upload.

Configuring Size Unit and Range
-------------------------------

On the setup page, configure the size unit you want to use for splitting the documents into fragments. When you select a new unit from the :guilabel:`Unit for Size` dropdown, the :guilabel:`Fragment Range` below will update with the recommended range.

The size unit should match the transformation method you intend to use, allowing the splitting algorithm to choose optimal fragment sizes. For example, if you plan to transform the text using the *GPT-4o language model*, select "Tokens for GPT-4o" with the recommended range.

- :guilabel:`Minimum Size`: The minimum size a fragment should be. Depending on the situation, the splitter may need to create smaller fragments.
- :guilabel:`Maximum Size`: The maximum size of a fragment. If the splitter cannot keep fragments smaller or equal to this size, the splitting process will stop with an error.

Document List Overview
----------------------

The document list shows all documents found in your import. Here are the columns you'll see:

- :guilabel:`Name`: The name of the document in your project. You can edit this to simplify or shorten names, but remember that these names will also be used for export.
- :guilabel:`Folder`: The folder where the document will be stored in your project. This can also be edited.
- :guilabel:`Document Syntax`: The detected document syntax. Choosing the correct syntax is crucial, as the splitting algorithm depends on it. For example, the algorithm for Markdown files differs from that for Python source code.
- :guilabel:`Planned Action`: Indicates whether the document will be added to the project (:guilabel:`Add`) or ignored (:guilabel:`Ignore`).

Click the green :guilabel:`Generate Preview` button at the end of the document list to proceed with the assistant.

The Import Preview
==================

*More documentation is coming soon*
