from collections import defaultdict
from pathlib import Path

from analyticq.util import path_to_str


class CodebaseMetricsCollector:

    def __init__(self) -> None:
        self.languages_stasts = defaultdict(lambda : {
            "count": 0,
            "total_size": 0,
            "files": [],
            "largest_file": None,
            "smallest_file": None
        })

        self.excluded_dirs = []
        self.excluded_files = []
        self.total_files = 0
        self.total_size = 0
        self.excluded_file_count = 0
        self.excluded_file_size = 0

    def _update_largest_file(self, file_path: Path, language: str, size: int):
        largest_file = self.languages_stasts[language]["largest_file"]
        if largest_file is None or size > largest_file["size"]:
            self.languages_stasts[language]["largest_file"] = {
                "path": path_to_str(file_path),
                "size" : size
            }

    def _update_smallest_file(self, file_path: Path, language: str, size: int):
        smallest_file = self.languages_stasts[language]["smallest_file"]
        if smallest_file is None or size < smallest_file["smallest_file"]:
            self.languages_stasts[language]["smallest_file"] = {
                "path": path_to_str(file_path),
                "size": size
            }

    def add_file_statistics(self, file_path: Path, language: str, size: int):
        self.languages_stasts[language]["count"] += 1
        self.languages_stasts[language]["total_size"] += size
        self.languages_stasts[language]["files"].append(path_to_str(file_path))

        self._update_largest_file(file_path, language, size)
        self._update_smallest_file(file_path, language, size)

        self.total_files += 1
        self.total_size += size

    def add_excluded_file(self, file_path: Path, size: int):
        self.excluded_files.append(str(file_path))
        self.excluded_file_count += 1
        self.excluded_file_size += size

    def add_excluded_dir(self, dir_path: Path):
        self.excluded_dirs.append(path_to_str(dir_path))

    def compute_languages_metrics(self):
        languages_metrics = {}
        for lang, data in self.languages_stasts.items():
            languages_metrics[lang] = {
                "file_count": data["count"],
                "total_size": data["total_size"],
                "largest_file": data["largest_file"],
                "average_size": data["total_size"] / data["count"] if data["count"] > 0 else 0,
                "percentage_files": (data["count"] / self.total_files) * 100 if self.total_files > 0 else 0,
                "smallest_file": data["smallest_file"]
            }
        return languages_metrics

    def get_metrics_report(self):
        return {
            "language_statistics": self.compute_languages_metrics(),
            "total_files_analyzed": self.total_files,
            "total_size_analyzed": self.total_size,
            "excluded_directories": self.excluded_dirs,
            "excluded_files": {
                "count": self.excluded_file_count,
                "total_size": self.excluded_file_size,
                "files": self.excluded_files,
            },
        }
