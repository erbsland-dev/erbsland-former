
.. _quick-start:
.. index::
    !single: Quick Start

===========
Quick Start
===========

What is ErbslandFORMER?
=======================

*ErbslandFORMER* is a web based tool, for individuals, small teams or companies to reliable process large amounts of text. Processing can be done using ChatGPT prompts, regular expressions or any custom developed extension. The imported documents are automatically split into text fragments, suitable for the chosen processing method. After processing, the individual results can be reviewed, approved or rejected. New revisions for additional processing can be created and finally the processed documented exported.

Install the Application
=======================

Have a look in the chapter :ref:`installation` for ways to install the application on a server or on your local machine.

Basic Workflow
==============

.. figure:: /images/basic-workflow.svg
    :width: 100%

*ErbslandFORMER* provides all tools for a classic document processing workflow. You first create a new project and import documents into it. Next, the documents are transformed using one more more transformation profiles you prepared. You review the results of the transformation and accept or reject them. If you do complex transformations, you create a new revision and do more transformations. If you are satisfied with the result, you export the documents and re-integrate them.

Visual Walkthrough
==================

In this visual walkthrough, you will see how Sphinx-based documentation is translated from English to German using ChatGPT-4 with just a few clicks. This example uses the file :file:`erbsland_qt_toml.zip`, which is included in the distribution and located in the :file:`backend/tests/data` folder.

After a fresh installation, entering your server's address in your browser will bring you to the login screen.

.. figure:: /images/walkthrough/walkthrough_00001.webp
    :width: 100%

Log in with the credentials you set up during installation or the ones provided by your system administrator.

.. figure:: /images/walkthrough/walkthrough_00002.webp
    :width: 100%

If you don't have any projects yet, you will see an empty project overview. Click on :guilabel:`Add New Project` to start a new project.

.. figure:: /images/walkthrough/walkthrough_00003.webp
    :width: 100%

The :guilabel:`Add New Project` form appears, where you can give the project a custom name. In this example, we name the project "Erbsland TOML Qt". There is also a field for a brief description, which is helpful for team projects.

.. figure:: /images/walkthrough/walkthrough_00004.webp
    :width: 100%

After clicking on :guilabel:`Create Project`, you will enter the new, empty project. To import documents, click on :guilabel:`Import Documents` to start the import assistant.

.. figure:: /images/walkthrough/walkthrough_00005.webp
    :width: 100%

In the import assistant, you can upload individual files or a ZIP archive of a whole project. Select `erbsland_qt_toml.zip` and click on :guilabel:`Upload File` to start the upload.

.. figure:: /images/walkthrough/walkthrough_00006.webp
    :width: 100%

The application analyzes the uploaded file and continues with the setup form. Here, you select the primary splitting unit and size range for the uploaded files. Choose "Tokens for GPT-4", with a text fragment range of 200 to 4048 tokens, which is recommended for this language model.

Below, a list of each file, including name, folder, detected document syntax, and actions, is displayed. You can change the names, paths, and settings individually for the import or remove files you don't need. For this example, we use the defaults.

.. figure:: /images/walkthrough/walkthrough_00007.webp
    :width: 100%

Click on :guilabel:`Create Preview` to process all files and create a preview of how the documents will be imported, including the exact splitting points. Review the created fragments and, if satisfied, click on :guilabel:`Import Files` to start the import.

.. figure:: /images/walkthrough/walkthrough_00008.webp
    :width: 100%

The import is completed, and a table with statistics about the import is displayed. Click on :guilabel:`Close and Continue to Project` to return to the project.

.. figure:: /images/walkthrough/walkthrough_00009.webp
    :width: 100%

The project is no longer empty, and you can see the imported folder structure with all documents in an unprocessed state.

.. figure:: /images/walkthrough/walkthrough_00010.webp
    :width: 100%

Since there are no transformation profiles yet, click on :guilabel:`Transformer` to open the transformer profiles page.

.. figure:: /images/walkthrough/walkthrough_00011.webp
    :width: 100%

The page is empty, so click on :guilabel:`Add Transformer Profile` to create a new transformer profile.

.. figure:: /images/walkthrough/walkthrough_00012.webp
    :width: 100%

Name the profile "Translate English to German" and select the "GPT Text Processor" for the transformation. Click on :guilabel:`Add Transformer Profile` to open the profile editor.

.. figure:: /images/walkthrough/walkthrough_00013.webp
    :width: 100%

The beta version comes with a predefined profile for this exact translation, so use the shown defaults and click on :guilabel:`Save and Close` to continue.

.. figure:: /images/walkthrough/walkthrough_00014.webp
    :width: 100%

The newly created profile is displayed in the profile list.

.. figure:: /images/walkthrough/walkthrough_00015.webp
    :width: 100%

Return to the home screen, where your project is displayed. Click on the project to open the document list.

.. figure:: /images/walkthrough/walkthrough_00016.webp
    :width: 100%

Select all documents from the `doc` folder that you want to translate and click on the :guilabel:`Start Transformation` button.

.. figure:: /images/walkthrough/walkthrough_00017.webp
    :width: 100%

The assistant opens with a preview of the selected documents. The latest transformation profile, "Translate English to German," is already selected. Click on :guilabel:`Continue` to proceed.

.. figure:: /images/walkthrough/walkthrough_00018.webp
    :width: 100%

Here, you can further filter the processed fragments, which is useful if you are running multiple transformation passes after previous failures or rejections. Keep the defaults and click on :guilabel:`Preview Transformation` to continue.

.. figure:: /images/walkthrough/walkthrough_00019.webp
    :width: 100%

A list of all documents and fragments to be transformed is displayed. If everything looks good, click on :guilabel:`Start Transformation` to begin the process.

.. figure:: /images/walkthrough/walkthrough_00020.webp
    :width: 100%

The transformation process may take some time, depending on the speed of the selected language model. While the text fragments are processed, you will see a status update with estimated times and running costs if applicable. These processes run in the background, so you can close your browser and check back later.

.. figure:: /images/walkthrough/walkthrough_00021.webp
    :width: 100%

After a few minutes, the transformation is complete, and a page with statistics about the transformation is displayed. Click on :guilabel:`Close and Continue to Project` to return to the project.

.. figure:: /images/walkthrough/walkthrough_00022.webp
    :width: 100%

The project status bars have changed, showing which documents have been processed and if there were any failed transformations. In this example, all transformations were successful. Click on :guilabel:`Review Pending Fragments` to start reviewing the changes.

.. figure:: /images/walkthrough/walkthrough_00023.webp
    :width: 100%

A handy diff view displays the changed lines. You can click on "Reject" or "Approve" to mark the text fragments accordingly. This allows you to quickly review all changes and address any rejected ones later. In this example, all changes were acceptable without manual edits.

.. figure:: /images/walkthrough/walkthrough_00024.webp
    :width: 100%

After reviewing the last fragment, you receive a message and return to the project.

.. figure:: /images/walkthrough/walkthrough_00025.webp
    :width: 100%

With all fragments reviewed and approved, it is time to export the results. Click on :guilabel:`Export Documents` to open the export assistant.

.. figure:: /images/walkthrough/walkthrough_00026.webp
    :width: 100%

Preview the selected documents to ensure the export settings are correct. Click on :guilabel:`Start Export` to begin the export process.

.. figure:: /images/walkthrough/walkthrough_00027.webp
    :width: 100%

The export is complete. You can now download the ZIP file with the exported documents and integrate the changes back into the project.

