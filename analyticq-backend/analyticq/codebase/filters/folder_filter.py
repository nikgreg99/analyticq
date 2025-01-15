from pathlib import Path


class FolderFilter:

    @staticmethod
    def is_empty_dir(directory_path: Path) -> bool:
        if directory_path.is_dir():
            return any(directory_path.iterdir())
        return False
