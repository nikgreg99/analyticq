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
        """Load the file filter configuration from the base configuration.

        The method retrieves the 'file_filter' configuration from the 'codebase' section
        of the AnalyticQ base configuration.

        Returns:
            None: The file filter configuration is stored in the class variable 'file_filter_conf'

        Raises:
            KeyError: If 'codebase' or 'file_filter' sections are not found in configuration
        """
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
        """Check if a file is hidden based on the operating system.

        This function determines whether a given file is hidden, with different implementation
        for Windows (NT) and Unix-like systems.

        Args:
            file_path (Path): The path to the file to check.

        Returns:
            bool: True if the file is hidden, False otherwise.

        Note:
            - On Windows (NT), it checks the file attributes for the hidden flag (0x2)
            - On Unix-like systems, it checks if the filename starts with a dot (.)
        """
        if os.name == "nt":
            return bool(file_path.stat().st_file_attributes & 2)
        else:
            return file_path.name.startswith(".")

    @staticmethod
    def is_empty_file(file_path: Path) -> bool:
        """
        Check if a file is empty based on its size.

        Args:
            file_path (Path): Path to the file to check.

        Returns:
            bool: True if the file is empty (size = 0 bytes), False otherwise.
        """
        return file_path.stat().st_size == 0

    @staticmethod
    def is_symlink_file(file_path: Path) -> bool:
        """
        Check if a file is a symbolic link.

        Args:
            file_path (Path): Path to the file to check.

        Returns:
            bool: True if the file is a symbolic link, False otherwise.
        """
        return file_path.is_symlink()

    @staticmethod
    def is_binary_file(file_path: Path) -> bool:
        """
        Determines if a file is binary by attempting to guess its file type.

        Args:
            file_path (Path): Path to the file to check

        Returns:
            bool: True if the file is detected as binary, False otherwise
                  Returns False in case of errors during file type detection
        """
        try:
            kind = filetype.guess(file_path)
            return True if kind is not None else False
        except Exception as e:
            logger.error(f"Failed to determine file type for {file_path}: {e}")
        return False

    @staticmethod
    def is_file_size_ok(file_path: Path) -> bool:
        """
        Check if the file size is within the allowed limit.

        This function compares the size of the file at the given path with the maximum
        allowed file size defined in FileFilter.

        Parameters:
            file_path (Path): Path object pointing to the file to check

        Returns:
            bool: True if file size is less than or equal to the maximum allowed size,
                  False otherwise

        Example:
            >>> file_path = Path('example.txt')
            >>> is_file_size_ok(file_path)
            True
        """
        max_file_size = FileFilter.max_size()
        file_size = file_path.stat().st_size
        return file_size <= max_file_size

    @staticmethod
    def is_extension_excluded(file_path: Path) -> bool:
        """
        Check if the file extension should be excluded based on predefined exclusion list.

        Args:
            file_path (Path): Path object representing the file path to check

        Returns:
            bool: True if the file extension is in the excluded list, False otherwise
        """
        return file_path.suffix.lower() in FileFilter.extensions_excluded()

    @staticmethod
    def is_filename_excluded(file_path: Path) -> bool:
        """
        Check if a file should be excluded based on its name.

        This function verifies if a given file path's name (case-insensitive) matches any
        of the excluded filenames defined in FileFilter.filename_excluded().

        Args:
            file_path (Path): Path object representing the file to check.

        Returns:
            bool: True if the filename should be excluded, False otherwise.
        """
        return file_path.name.upper() in FileFilter.filename_excluded()

    @staticmethod
    def is_relevant_file(file_path: Path) -> bool:
        """
        Determines if a file is relevant for analysis based on multiple criteria.

        Args:
            file_path (Path): Path object pointing to the file to be checked

        Returns:
            bool: True if the file is relevant for analysis, False otherwise
        """
        return (
            not FileFilter.is_empty_file(file_path)
            and not FileFilter.is_binary_file(file_path)
            and FileFilter.is_file_size_ok(file_path)
            and not FileFilter.is_extension_excluded(file_path)
            and not FileFilter.is_filename_excluded(file_path)
        )
