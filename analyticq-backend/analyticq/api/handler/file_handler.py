import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Tuple

from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file upload and validation."""

    SUPPORTED_EXTENSIONS = {'.zip', '.tar', '.gz'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    @classmethod
    async def process_uploaded_files(
        cls,
        files: List[UploadFile],
        analysis_id: str,
        tracker
    ) -> Tuple[List[str], List[str]]:
        """Process uploaded files and return temp paths and original filenames."""
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        temp_file_paths = []
        original_filenames = []

        try:
            for upload_file in files:
                cls._validate_file(upload_file)

                temp_path = await cls._save_temp_file(upload_file)
                temp_file_paths.append(temp_path)
                original_filenames.append(upload_file.filename)

                # Track temp files for cleanup
                cls._track_temp_file(tracker, analysis_id, temp_path, upload_file.filename)

            return temp_file_paths, original_filenames

        except Exception:
            # Cleanup on error
            cls._cleanup_temp_files(temp_file_paths)
            raise

    @classmethod
    def _validate_file(cls, upload_file: UploadFile):
        """Validate uploaded file format and size."""
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        file_ext = Path(upload_file.filename).suffix.lower()
        if file_ext not in cls.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {upload_file.filename}. "
                       f"Supported formats: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )

    @classmethod
    async def _save_temp_file(cls, upload_file: UploadFile) -> str:
        """Save uploaded file to temporary location."""
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await upload_file.read()

            if len(content) > cls.MAX_FILE_SIZE:
                temp_file.close()
                os.unlink(temp_file.name)
                raise HTTPException(
                    status_code=413,
                    detail=f"File {upload_file.filename} exceeds maximum size limit"
                )

            temp_file.write(content)
            return temp_file.name

    @classmethod
    def _track_temp_file(cls, tracker, analysis_id: str, temp_path: str, filename: str):
        """Track temporary file for cleanup."""
        record = tracker.get_analysis(analysis_id)
        if record:
            record.temp_files.append(temp_path)
            record.original_filenames.append(filename)

    @classmethod
    def _cleanup_temp_files(cls, temp_file_paths: List[str]):
        """Clean up temporary files on error."""
        for temp_path in temp_file_paths:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Could not clean up temp file {temp_path}: {e}")
