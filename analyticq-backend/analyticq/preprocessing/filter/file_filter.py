import logging
import os
from pathlib import Path

import filetype
from analyticq.config import AnalyticQBaseConfig

logger = logging.getLogger(__name__)


class FileFilter:

    file_filter_conf: dict = None

    @classmethod
    def load_file_filter_conf(cls):
        codebase_conf = AnalyticQBaseConfig.get("codebase")
        cls.file_filter_conf = codebase_conf.get("file_filter")

    @classmethod
    def get_file_filter_conf(cls) -> dict:
        if cls.file_filter_conf is None:
            cls.load_file_filter_conf()
        return cls.file_filter_conf

    @classmethod
    def extensions_excluded(cls):
        return set(cls.get_file_filter_conf().get("extensions_excluded", []))

    @classmethod
    def filename_excluded(cls):
        return set(cls.get_file_filter_conf().get("filenames_excluded", []))

    @classmethod
    def max_size(cls) -> int:
        return cls.get_file_filter_conf().get("max_file_size", 50 * 1024 * 1024)

    @staticmethod
    def is_hidden_file(file_path: Path) -> bool:
        if os.name == "nt":
            return bool(file_path.stat().st_file_attributes & 2)
        else:
            return file_path.name.startswith(".")

    @staticmethod
    def is_empty_file(file_path: Path) -> bool:
        return file_path.stat().st_size == 0

    @staticmethod
    def is_symlink_file(file_path: Path) -> bool:
        return file_path.is_symlink()

    @staticmethod
    def is_binary_file(file_path: Path) -> bool:
        try:
            kind = filetype.guess(file_path)
            return True if kind is not None else False
        except Exception as e:
            logger.error(f"Failed to determine file type for {file_path}: {e}")
        return False

    @staticmethod
    def is_file_size_ok(file_path: Path) -> bool:
        max_file_size = FileFilter.max_size()
        file_size = file_path.stat().st_size
        return file_size <= max_file_size

    @staticmethod
    def is_extension_excluded(file_path: Path) -> bool:
        return file_path.suffix.lower() in FileFilter.extensions_excluded()

    @staticmethod
    def is_filename_excluded(file_path: Path) -> bool:
        return file_path.name.upper() in FileFilter.filename_excluded()

    def is_relevant_file(file_path: Path) -> bool:
        return (
            not FileFilter.is_empty_file(file_path)
            and not FileFilter.is_binary_file(file_path)
            and FileFilter.is_file_size_ok(file_path)
            and not FileFilter.is_extension_excluded(file_path)
            and not FileFilter.is_filename_excluded(file_path)
        )
