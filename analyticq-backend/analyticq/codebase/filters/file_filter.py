import os
from pathlib import Path


class FileFilter:

    @staticmethod
    def is_hidden(file_path: Path) -> bool:
        if os.name == "nt":
            return bool(file_path.stat().st_file_attributes & 2)
        else:
            return file_path.name.startswith(".")

    @staticmethod
    def is_empty_file(file_path: Path) -> bool:
        return file_path.stat.st_size == 0
