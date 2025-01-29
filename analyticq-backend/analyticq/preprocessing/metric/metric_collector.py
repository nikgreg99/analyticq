import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, TypedDict

from analyticq.util import PathUtil

logger = logging.getLogger(__name__)


@dataclass
class FileMetrics:
    """Represents metrics for a single file."""
    path: str
    size: int
    loc: Optional[int] = None


class LanguageStats(TypedDict):
    """Type definition for language statistics."""
    count: int
    total_size: int
    files: List[Dict[str, str | int]]
    largest_file: Optional[Dict[str, str | int]]
    smallest_file: Optional[Dict[str, str | int]]


class ExcludedFiles(TypedDict):
    """Type definition for excluded files statistics."""
    count: int
    total_size: int
    files: List[str]


class CodebaseStatistics(TypedDict):
    """Type definition for complete codebase statistics."""
    language_stats: Dict[str, LanguageStats]
    total_files: int
    total_size: int
    excluded_files: ExcludedFiles
    excluded_dirs: List[str]


@dataclass
class CodebaseMetricsCollector:
    """Collects and manages codebase metrics including file sizes, language statistics, and exclusions."""

    language_stats: DefaultDict[str, LanguageStats] = field(default_factory=lambda: defaultdict(
        lambda: {
            "count": 0,
            "total_size": 0,
            "files": [],
            "largest_file": None,
            "smallest_file": None
        }
    ))
    excluded_dirs: List[str] = field(default_factory=list)
    excluded_files: List[str] = field(default_factory=list)
    total_files: int = 0
    total_size: int = 0
    excluded_file_count: int = 0
    excluded_file_size: int = 0

    def _update_file_size_extremes(self, file_metrics: FileMetrics, language: str) -> None:
        """
        Update the largest and smallest file records for a given language.

        Args:
            file_metrics: FileMetrics object containing file information
            language: Programming language of the file
        """
        stats = self.language_stats[language]
        file_info = {"path": file_metrics.path, "size": file_metrics.size}

        if stats["largest_file"] is None or file_metrics.size > stats["largest_file"]["size"]:
            stats["largest_file"] = file_info

        if stats["smallest_file"] is None or file_metrics.size < stats["smallest_file"]["size"]:
            stats["smallest_file"] = file_info

    def add_file_statistics(self, file_path: Path, language: str, size: Optional[int] = None, loc: Optional[int] = None) -> None:
        """
        Add statistics for a single file.

        Args:
            file_path: Path to the file
            language: Programming language of the file
            size: File size in bytes (optional, will be calculated if not provided)
            loc: Lines of code (optional)

        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        actual_size = size if size is not None else file_path.stat().st_size
        file_metrics = FileMetrics(
            path=PathUtil.path_to_str(file_path),
            size=actual_size,
            loc=loc
        )

        lang_stats = self.language_stats[language]
        lang_stats["count"] += 1
        lang_stats["total_size"] += actual_size
        lang_stats["files"].append({
            "file_path": file_metrics.path,
            "loc": loc
        })

        self.total_files += 1
        self.total_size += actual_size

        self._update_file_size_extremes(file_metrics, language)

        logger.debug(f"Added statistics for file: {file_path} (language: {language}, size: {actual_size})")

    def add_excluded_file(self, file_path: Path, size: Optional[int] = None) -> None:
        """
        Add an excluded file to the statistics.

        Args:
            file_path: Path to the excluded file
            size: File size in bytes (optional, will be calculated if not provided)

        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        actual_size = size if size is not None else file_path.stat().st_size
        self.excluded_files.append(str(file_path))
        self.excluded_file_count += 1
        self.excluded_file_size += actual_size

        logger.debug(f"Added excluded file: {file_path} (size: {actual_size})")

    def add_excluded_dir(self, dir_path: Path) -> None:
        """
        Add an excluded directory to the statistics.

        Args:
            dir_path: Path to the excluded directory

        Raises:
            NotADirectoryError: If the path is not a directory
        """
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        self.excluded_dirs.append(PathUtil.path_to_str(dir_path))
        logger.debug(f"Added excluded directory: {dir_path}")

    def get_collected_data(self) -> CodebaseStatistics:
        """
        Return the collected codebase statistics.

        Returns:
            Dict containing all collected statistics
        """
        return {
            "language_stats": dict(self.language_stats),
            "total_files": self.total_files,
            "total_size": self.total_size,
            "excluded_files": {
                "count": self.excluded_file_count,
                "total_size": self.excluded_file_size,
                "files": self.excluded_files,
            },
            "excluded_dirs": self.excluded_dirs,
        }
