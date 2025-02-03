import os
from pathlib import Path

from analyticq.config import AnalyticQBaseConfig
from analyticq.util import PathUtil


class DirFilter:

    dir_filter_conf: dict = None

    @classmethod
    def load_dir_filter_conf(cls):
        """
        Loads directory filter configuration from the codebase configuration.

        This class method retrieves the directory filter configuration from the base codebase
        configuration and stores it in the class variable dir_filter_conf.

        Returns:
            None: The method sets the class variable dir_filter_conf directly
        """
        codebase_conf = AnalyticQBaseConfig.get("codebase")
        cls.dir_filter_conf = codebase_conf.get("dir_filter")

    @classmethod
    def get_dir_filter_conf(cls) -> dict:
        if cls.dir_filter_conf is None:
            cls.load_dir_filter_conf()
        return cls.dir_filter_conf

    @classmethod
    def excluded_dirs(cls) -> dict:
        return set(cls.get_dir_filter_conf().get("excluded_dirs", []))

    @classmethod
    def max_depth(cls) -> dict:
        return cls.get_dir_filter_conf().get("max_depth", 5)

    @staticmethod
    def is_empty_dir(dir_path: Path) -> bool:
        """
        Check if a directory is empty.

        This function verifies if the given path is a directory and if it contains no files or subdirectories.

        Args:
            dir_path (Path): Path object pointing to the directory to check.

        Returns:
            bool: True if the directory exists and is empty, False otherwise.
        """
        return dir_path.is_dir() and not any(dir_path.iterdir())

    @staticmethod
    def is_excluded_dir(dir_path: Path) -> bool:
        """
        Check if a directory should be excluded based on its name.

        The function examines the last directory name in the path and checks if it matches
        any of the predefined excluded directory names.

        Args:
            dir_path (Path): Path object representing the directory path to check

        Returns:
            bool: True if the directory should be excluded, False otherwise
        """
        last_folder = PathUtil.get_last_dir_name(dir_path)
        return last_folder in DirFilter.excluded_dirs()

    @staticmethod
    def is_max_depth(dir_path: Path) -> bool:
        """
        Check if a directory path exceeds the maximum allowed depth.

        Args:
            dir_path (Path): The directory path to check.

        Returns:
            bool: True if the directory depth exceeds the maximum allowed depth, False otherwise.

        Note:
            The depth is calculated by counting path segments minus 1. For example:
            - '/home/user' has depth 1 (3-1-1)
            - '/home/user/docs' has depth 2 (4-1-1)
        """
        return len(dir_path.parts) - 1 > DirFilter.max_depth()

    @staticmethod
    def is_read_only_dir(dir_path: Path) -> bool:
        """
        Check if a directory is read-only.

        Args:
            dir_path (Path): Path to the directory to check.

        Returns:
            bool: True if directory is read-only, False if it is writable.
        """
        return not os.access(dir_path, os.W_OK)

    @staticmethod
    def is_non_local_dir(dir_path: Path) -> bool:
        """
        Check if a directory path corresponds to a mount point.

        This function determines whether a given directory path is a mount point,
        which typically indicates a non-local directory (e.g., network drives, mounted volumes).

        Args:
            dir_path (Path): The directory path to check.

        Returns:
            bool: True if the directory is a mount point, False otherwise.
        """
        return os.path.ismount(dir_path)

    @staticmethod
    def is_symlink(dir_path: Path) -> bool:
        """
        Check if a directory path is a symbolic link.

        Args:
            dir_path (Path): The directory path to check.

        Returns:
            bool: True if the path is a symbolic link, False otherwise.
        """
        return dir_path.is_symlink()

    @staticmethod
    def is_relevant_dir(dir_path: Path) -> bool:
        """Determine if a directory path should be excluded from processing.

        This function checks various conditions to decide if a directory should be considered
        relevant for further processing or should be filtered out based on multiple criteria.

        Args:
            dir_path (Path): Path object representing the directory to check.

        Returns:
            bool: True if the directory should be excluded (meets any exclusion criteria),
                  False if the directory should be processed.

        """
        return (
            DirFilter.is_empty_dir(dir_path)
            or DirFilter.is_excluded_dir(dir_path)
            or DirFilter.is_max_depth(dir_path)
            or DirFilter.is_read_only_dir(dir_path)
            or DirFilter.is_non_local_dir(dir_path)
            or DirFilter.is_symlink(dir_path)
        )
