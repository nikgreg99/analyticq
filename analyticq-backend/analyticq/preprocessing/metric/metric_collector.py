import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Dict, Generator, List

from analyticq.util import PathUtil

logger = logging.getLogger(__name__)


@dataclass
class FileStastics:
    path: str
    size: int


class CodebaseMetricsCollector:

    def __init__(self) -> None:
        self.language_stats = defaultdict(lambda : {
            "count": 0,
            "total_size": 0,
            "files": [],
            "largest_file": None,
            "smallest_file": None
        })

        self.excluded_dirs: List[str] = []
        self.excluded_files: List[str] = []
        self.total_files: int = 0
        self.total_size: int = 0
        self.excluded_file_count: int = 0
        self.excluded_file_size: int = 0
        self.lock = Lock()

    def _update_file_size_extremes(self, file_path: Path, language: str, size: int):
        stats = self.language_stats[language]
        file_info = {"path": PathUtil.path_to_str(file_path), "size": size}

        if stats["largest_file"] is None or size > stats["largest_file"]["size"]:
            stats["largest_file"] = file_info

        if stats["smallest_file"] is None or size < stats["smallest_file"]["size"]:
            stats["smallest_file"] = file_info

    def _process_file(self, file_path: Path, language: str):
        size = file_path.stat().st_size

        with self.lock:
            self.language_stats[language]["count"] += 1
            self.language_stats[language]["total_size"] += size
            self.language_stats[language]["files"].append(PathUtil.path_to_str(file_path))

            self.total_files += 1
            self.total_size += size

        self._update_file_size_extremes(file_path, language, size)

    def _batch_generator(self, files: List[Path], batch_size: int) -> Generator[List[Path], None, None]:
        """Generator function that yields batches of files."""
        for i in range(0, len(files), batch_size):
            yield files[i:i + batch_size]

    def add_files_parallel(self, files: List[Path], language: str, batch_size: int = 1000, max_workers: int = 8):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for batch in self._batch_generator(files, batch_size):
                for file in batch:
                    futures.append(executor.submit(self._process_file, file, language))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error processing file: {e}")

    def add_excluded_file(self, file_path: Path, size: int):
        with self.lock:
            self.excluded_files.append(str(file_path))
            self.excluded_file_count += 1
            self.excluded_file_size += size

    def add_excluded_dir(self, dir_path: Path):
        self.excluded_dirs.append(PathUtil.path_to_str(dir_path))

    def get_collected_data(self) -> Dict:
        """Return raw collected statistics."""
        return {
            "language_stats": self.language_stats,
            "total_files": self.total_files,
            "total_size": self.total_size,
            "excluded_files": {
                "count": self.excluded_file_count,
                "total_size": self.excluded_file_size,
                "files": self.excluded_files,
            },
            "excluded_dirs": self.excluded_dirs,
        }
