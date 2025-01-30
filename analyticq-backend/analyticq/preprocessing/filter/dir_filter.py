import os
from pathlib import Path

from analyticq.config import AnalyticQBaseConfig
from analyticq.util import PathUtil


class DirFilter:

    dir_filter_conf: dict = None

    @classmethod
    def load_dir_filter_conf(cls):
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
        return dir_path.is_dir() and not any(dir_path.iterdir())

    @staticmethod
    def is_excluded_dir(dir_path: Path) -> bool:
        last_folder = PathUtil.get_last_dir_name(dir_path)
        return last_folder in DirFilter.excluded_dirs()

    @staticmethod
    def is_max_depth(dir_path: Path) -> bool:
        return len(dir_path.parts) - 1 > DirFilter.max_depth()

    @staticmethod
    def is_read_only_dir(dir_path: Path) -> bool:
        return not os.access(dir_path, os.W_OK)

    @staticmethod
    def is_non_local_dir(dir_path: Path) -> bool:
        return os.path.ismount(dir_path)

    @staticmethod
    def is_symlink(dir_path: Path) -> bool:
        return dir_path.is_symlink()

    @staticmethod
    def is_relevant_dir(dir_path: Path) -> bool:
        return (
            DirFilter.is_empty_dir(dir_path)
            or DirFilter.is_excluded_dir(dir_path)
            or DirFilter.is_max_depth(dir_path)
            or DirFilter.is_read_only_dir(dir_path)
            or DirFilter.is_non_local_dir(dir_path)
            or DirFilter.is_symlink(dir_path)
        )
