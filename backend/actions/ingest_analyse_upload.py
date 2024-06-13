#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later

import logging
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Optional
from zipfile import ZipFile, BadZipFile, ZipInfo

import unicodedata
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from backend.actions.ingest_base import IngestBase
from backend.models import IngestDocument
from backend.enums.ingest_step import IngestStep
from backend.enums.ingest_planed_action import IngestPlanedAction
from backend.syntax_handler import syntax_manager
from backend.tools.regular_expressions import (
    RE_PROBLEMATIC_FILE_PATH_CHARACTERS,
    RE_PROBLEMATIC_FILE_NAME_CHARACTERS,
)
from tasks.actions.exception import ActionError


class IngestAnalyzeUpload(IngestBase):
    name = "ingest_analyze_upload"
    progress_title = _("Analyzing Uploaded Files")
    progress_subject = _("Analysis")

    RE_ILLEGAL_PATH_ELEMENTS = re.compile(R"^\.\.|^\./|^/|/\.\./|/\./|/\.\.$|/\.$")

    def __init__(self, task_id: str, log: logging.Logger):
        super().__init__(task_id, log)
        self.uploaded_file: Optional[Path] = None
        self.ingest_file_index = 0
        self.documents_to_add = 1
        self.document_count = 0

    def run(self, input_data: dict) -> None:
        self.log_info(_("Start analyzing the upload."))
        self.set_progress(float(self.document_count), float(self.documents_to_add), _("Analyzing Uploaded Files"))
        with transaction.atomic():
            self.set_db_object_from_input_data(input_data)
            if self.ingest_assistant.step != IngestStep.ANALYSIS_RUNNING:
                raise ActionError(_("The ingest operation is in the wrong state."))
            self.verify_upload()
            self.create_working_directory()
        with transaction.atomic():
            try:
                if self.uploaded_file.suffix.lower() == ".zip":
                    self.extract_zip()
                else:
                    self.copy_and_add_single_document()
                # Successfully analyzed and unpacked the uploaded file.
                self.ingest_assistant.step = IngestStep.SETUP
                self.ingest_assistant.save()
                self.log_info(_("Successfully analyzed the upload."))
                self.set_progress(
                    float(self.document_count), float(self.documents_to_add), _("Successfully analyzed the upload.")
                )
            except Exception:
                self.log_error(_("There were problems analyzing the upload. Removing extracted files."))
                if self.working_directory and self.working_directory.is_dir():
                    shutil.rmtree(self.working_directory, ignore_errors=True)
                raise

    def verify_upload(self):
        """
        Verify the uploaded document if it meets the limits.
        """
        self.uploaded_file = Path(self.ingest_assistant.uploaded_file.path)
        if not self.uploaded_file.is_file():
            raise ActionError(_("The uploaded file seems not to be a file (anymore)."))
        if self.uploaded_file.lstat().st_size > settings.BACKEND_INGEST_UPLOAD_FILE_SIZE:
            raise ActionError(
                _("The uploaded file exceeds the maximum allowed size of %(size)d bytes.")
                % {"size": settings.BACKEND_INGEST_UPLOAD_FILE_SIZE}
            )
        if self.uploaded_file.lstat().st_size > settings.BACKEND_INGEST_DOCUMENT_SIZE:
            raise ActionError(
                _("The uploaded file exceeds the maximum allowed size of %(size)d bytes.")
                % {"size": settings.BACKEND_INGEST_DOCUMENT_SIZE}
            )

    def create_working_directory(self):
        """
        Create a new temporary working directory.

        :return: The created temporary path.
        """
        ingest_dir = Path(settings.BACKEND_WORKING_DIR) / f"ingest_{self.ingest_assistant.pk}"
        try:
            ingest_dir.mkdir(parents=True)
            self.working_directory = ingest_dir
            self.ingest_assistant.working_directory = (
                ingest_dir  # Keep that so it get removed when the assistant is deleted.
            )
            self.ingest_assistant.save()
        except Exception as error:
            self.log_debug(f"Failed to create directory. path={ingest_dir} error={error}")
            raise ActionError(_("The working directory cannot be accessed."))

    def create_working_file_path(self) -> Path:
        """
        Create a new path for a document that will get imported.

        :return: The new path.
        """
        self.ingest_file_index += 1
        return self.working_directory / f"file_{self.ingest_file_index:04d}.data"

    def copy_and_add_single_document(self):
        """
        Copy a single document uploaded.
        """
        dst_path = self.create_working_file_path()
        try:
            shutil.copyfile(self.uploaded_file, dst_path, follow_symlinks=False)
        except Exception as error:
            self.log_debug(f"Failed to copy uploaded file. src={self.uploaded_file} dst={dst_path} error={error}")
            raise ActionError(_("There was a problem copy the uploaded file."))
        file_name = self.uploaded_file.name
        file_name = unicodedata.normalize("NFC", file_name)
        file_name = RE_PROBLEMATIC_FILE_NAME_CHARACTERS.sub("_", file_name)
        self.add_document(dst_path, Path(file_name))
        self.document_count += 1

    def extract_zip(self):
        """
        Scan and extract files from a ZIP file.
        """
        self.scan_zip_metadata()
        self.extract_zip_contents()

    def scan_zip_metadata(self):
        """
        In a first pass, only scan the zip for any problematic content.
        """
        self.log_info(_("Scanning the ZIP file metadata"))

        def handle_zip_entry(file_info: ZipInfo, zip_file: ZipFile, original_path: Path) -> int:
            return file_info.file_size

        self.iterate_zip_info(handle_zip_entry)

    def extract_zip_contents(self):
        self.log_info(_("Extracting ZIP files"))
        self.set_progress(float(self.document_count), float(self.documents_to_add), _("Extracting ZIP files"))

        def handle_zip_entry(file_info: ZipInfo, zip_file: ZipFile, original_path: Path) -> int:
            target_path = self.create_working_file_path()
            maximum_size = settings.BACKEND_INGEST_DOCUMENT_SIZE
            byte_count = 0
            with zip_file.open(file_info, "r") as src_fp:
                with target_path.open("wb") as dst_fp:
                    while block := src_fp.read(4096):
                        dst_fp.write(block)
                        byte_count += len(block)
                        if byte_count > maximum_size:
                            raise ActionError(_("A file in the ZIP archive exceeds the maximum size."))
            if file_info.file_size != byte_count:
                raise ActionError(_("The metadata of a file in the ZIP archive is inconsistent."))
            self.add_document(target_path, original_path)
            self.document_count += 1
            self.set_progress(float(self.document_count), float(self.documents_to_add), _("Extracting ZIP files"))
            return byte_count

        self.iterate_zip_info(handle_zip_entry)

    def iterate_zip_info(self, handle_zip_entry: Callable[[ZipInfo, ZipFile, Path], int]):
        """
        Iterate over a zip file.

        :param handle_zip_entry: A function to handle the zip entry.
        """
        try:
            normalized_names: dict[str, int] = {}
            total_size = 0
            file_count = 0
            # Do a first scan to stop the import of suspicious ZIP files before even extracting data from it.
            with ZipFile(self.uploaded_file, mode="r") as zip_file:
                for file_info in zip_file.infolist():
                    if file_info.is_dir():
                        continue
                    if file_info.file_size <= 0:
                        continue  # Skipping zero byte files.
                    file_path = file_info.filename
                    file_path = unicodedata.normalize("NFC", file_path)
                    file_path = RE_PROBLEMATIC_FILE_PATH_CHARACTERS.sub("_", file_path)
                    file_path = file_path.replace("\\", "/")
                    if file_path.startswith("/"):
                        file_path = file_path[1:]
                    technical_details = _("Path: %(path)s Size: %(size)d bytes") % {
                        "path": file_path,
                        "size": file_info.file_size,
                    }
                    if len(file_path) > 250:
                        raise ActionError(
                            _("The ZIP archive contains files paths that exceed the maximum length."),
                            technical_details=technical_details,
                        )
                    if self.RE_ILLEGAL_PATH_ELEMENTS.search(file_path):
                        raise ActionError(
                            _("The ZIP archive contains problematic paths."),
                            technical_details=technical_details,
                        )
                    if file_info.file_size > settings.BACKEND_INGEST_DOCUMENT_SIZE:
                        raise ActionError(
                            _("The ZIP archive contains files that are too large to process."),
                            technical_details=technical_details,
                        )
                    if file_path.casefold() in normalized_names:
                        raise ActionError(
                            _("The ZIP archive contains files with overlapping names."),
                            technical_details=technical_details,
                        )
                    normalized_names[file_path.casefold()] = 1
                    path = Path(file_path)
                    file_name = path.name.strip()
                    if file_name.startswith("."):
                        continue  # Skipping hidden files
                    file_count += 1
                    if file_count > settings.BACKEND_INGEST_FILE_COUNT:
                        raise ActionError(
                            _(
                                "The ZIP archive exceeds the maximum number of files that are allowed "
                                "to import at once. The maximum number is %(count)d files."
                            )
                            % {"count": settings.BACKEND_INGEST_FILE_COUNT},
                            technical_details=technical_details,
                        )
                    total_size += handle_zip_entry(file_info, zip_file, path)
                    if total_size > settings.BACKEND_INGEST_UPLOAD_FILE_SIZE:
                        raise ActionError(
                            _("The contents of the ZIP file exceeds the maximum size of %(size)d bytes.")
                            % {"size": settings.BACKEND_INGEST_UPLOAD_FILE_SIZE},
                            technical_details=technical_details,
                        )
            if file_count == 0:
                raise ActionError(_("The ZIP file contains no files that can be imported."))
            if total_size == 0:
                raise ActionError(_("The ZIP file contains no data to be imported."))
            self.documents_to_add = file_count
        except BadZipFile as error:
            self.log_error(_("The uploaded ZIP file seems to be damaged: %(error)s") % {"error": str(error)})
            raise ActionError(_("The uploaded ZIP file was damaged."))

    def add_document(self, working_path: Path, original_path: Path):
        """
        Analyze a single document and add it to the ingest operation.

        :param working_path: The path to the file.
        :param original_path: The original path of the file.
        """
        syntax_identifier = syntax_manager.detect_file_syntax(working_path, original_path)
        folder = original_path.parent.as_posix()
        if folder == ".":
            folder = ""
        planed_action = IngestPlanedAction.ADD
        if not syntax_identifier:
            planed_action = IngestPlanedAction.IGNORE
        name = RE_PROBLEMATIC_FILE_NAME_CHARACTERS.sub("", original_path.name.strip())
        IngestDocument.objects.create(
            ingest=self.ingest_assistant,
            local_path=working_path.relative_to(self.working_directory).as_posix(),
            name=name,
            folder=folder,
            document_syntax=syntax_identifier,
            planed_action=planed_action,
        )

    def on_failed(self, error: Exception) -> None:
        if self.ingest_assistant:
            self.ingest_assistant.delete()

    def on_stopped(self) -> None:
        if self.ingest_assistant:
            self.ingest_assistant.delete()
