#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
import shutil
from pathlib import Path

from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save

from backend.models.content_user import ContentUser
from backend.models.egress_assistant import EgressAssistant
from backend.models.fragment import Fragment
from backend.models.user_settings import UserSettings
from backend.models.document import Document
from backend.models.ingest_assistant import IngestAssistant
from backend.models.ingest_document import IngestDocument
from backend.models.project import Project
from backend.models.revision import Revision
from backend.models.fragment_edit import FragmentEdit
from backend.models.fragment_transformation import FragmentTransformation
from backend.storage import working_storage

logger = logging.getLogger(__name__)


def _delete_preview_documents_on_ingest_delete(sender, instance: IngestAssistant, **kwargs):
    # logger.debug("Removing preview documents after ingest operation was deleted.")
    try:
        project = instance.project
        revision = project.get_latest_revision()
        Document.objects.filter(revision=revision, is_preview=True).delete()
    except Project.DoesNotExist:
        # When the project was deleted, all documents are gone, just warn.
        logger.warning("After deleting ingest object, associated project was missing.")
    except Revision.DoesNotExist:
        # Without revision, there are no documents, so ignore it, just warn.
        logger.warning("After deleting ingest object, cannot find the latest revision to delete preview documents.")


def _create_profile_for_new_users(sender, instance: User, **kwargs):
    try:
        if instance.settings:
            return
    except UserSettings.DoesNotExist:
        pass
    UserSettings.objects.create(user=instance)


def _release_content_after_fragment_delete(sender, instance: ContentUser, **kwargs):
    """
    Make sure that content objects are properly released and deleted after a fragment gets deleted.
    """
    if instance.content is not None:
        instance.content.release()


def _delete_working_dir_on_egress_delete(sender, instance: EgressAssistant, **kwargs):
    """
    When the egress assistant is deleted (user clicks on done), make sure the working directory
    is deleted with the database object.

    :note: Make sure the specified path is a valid working directory.
    """
    if not instance.working_directory:
        logger.warning(f"The egress assistant ({instance.pk}) had an empty working directory when deleted. Ignored.")
        return
    path = Path(instance.working_directory)
    if not path.name.startswith("egress_"):
        logger.error(
            "The egress assistant ({instance.pk}) had a working directory that didn't started with 'egress_'. Ignored."
        )
        return
    shutil.rmtree(path, ignore_errors=True)


def _delete_temp_files_on_ingest_delete(sender, instance: IngestAssistant, **kwargs):
    """
    When the ingest assistant is deleted (user clicks on done), make sure the working directory
    and the uploaded file is deleted with the database object.

    :note: Make sure the specified path is a valid working directory.
    """
    # First delete any uploaded file if it exists (using the storage manager)
    if instance.uploaded_file.path:
        path = Path(instance.uploaded_file.path)
        working_storage.delete(path)
    # If there is a working directory set, delete it but make sure it starts with "ingest_".
    if not instance.working_directory:
        logger.warning(f"The ingest assistant ({instance.pk}) had an empty working directory when deleted. Ignored.")
        return
    path = Path(instance.working_directory)
    if not path.name.startswith("ingest_"):
        logger.error(
            "The ingest assistant ({instance.pk}) had a working directory that didn't started with 'ingest_'. Ignored."
        )
        return
    shutil.rmtree(path, ignore_errors=True)


def register_signals():
    """
    Register all signals for this app.
    """
    post_delete.connect(_delete_temp_files_on_ingest_delete, sender=IngestAssistant)
    post_delete.connect(_delete_preview_documents_on_ingest_delete, sender=IngestAssistant)
    post_delete.connect(_release_content_after_fragment_delete, sender=Fragment)
    post_delete.connect(_release_content_after_fragment_delete, sender=FragmentEdit)
    post_delete.connect(_release_content_after_fragment_delete, sender=FragmentTransformation)
    post_delete.connect(_delete_working_dir_on_egress_delete, sender=EgressAssistant)
    post_save.connect(_create_profile_for_new_users, sender=User)
