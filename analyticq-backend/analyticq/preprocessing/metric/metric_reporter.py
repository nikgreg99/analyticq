from pathlib import Path
from typing import Any, Dict, List, Optional

from dependency_injector.wiring import Provide, inject

from .metric_calculator import CodebaseMetricsCalculator
from .metric_collector import CodebaseMetricsCollector


class CodebaseMetricsReporter:

    @inject
    def __init__(self,
                 metric_collector: Provide[CodebaseMetricsCollector],
                 metric_calculator: Provide[CodebaseMetricsCalculator]):
        self.metric_collector = metric_collector
        self.metric_calculator = metric_calculator

    def add_excluded_file(self, file_path: Path, size: Optional[int] = None) -> None:
        """
        Add a file to the list of excluded files during the analysis.

        Args:
            file_path (Path): The path to the file that was excluded.
            size (Optional[int], optional): The size of the excluded file in bytes. Defaults to None.

        Returns:
            None
        """
        self.metric_collector.add_excluded_file(file_path, size)

    def add_excluded_dir(self, dir_path: Path) -> None:
        """
        Add a directory path to the list of excluded directories during metric collection.

        Args:
            dir_path (Path): The path of the directory to be excluded from metric collection.

        Returns:
            None
        """
        self.metric_collector.add_excluded_dir(dir_path)

    def add_file_statistics(self, file_path: Path, language: str, size: Optional[int] = None, loc: Optional[int] = None) -> None:
        """
        Add statistics for a specific file to the metric collector.

        Args:
            file_path (Path): Path to the file being analyzed
            language (str): Programming language of the file
            size (Optional[int], optional): Size of file in bytes. Defaults to None.
            loc (Optional[int], optional): Lines of code in file. Defaults to None.

        Returns:
            None
        """
        self.metric_collector.add_file_statistics(file_path, language, size, loc)

    def list_files_by_Languages(self, collected_data) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organizes file information by programming language.

        This method processes collected data and creates a dictionary where each key is a programming language
        and its value is a list of dictionaries containing information about files in that language.

        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary where:
                - Keys are programming language names (str)
                - Values are lists of dictionaries containing:
                    - 'file_path': Path to the file (str)
                    - 'loc': Lines of code (int or None)
                    - 'size': File size in bytes (int or None)
        """
        result = {}
        for lang, stasts in collected_data.items():
            result[lang] = []
            for file_info in stasts["files"]:
                file_entry = {
                    "file_path": file_info["file_path"],
                    "loc": file_info.get("loc", None),
                    "size": file_info.get("size", None)
                }
                result[lang].append(file_entry)
        return result

    def reset_metric_collector(self) -> None:
        """
        Reset the metric collector to its initial state.

        This method resets all collected metrics by calling the reset method of the metric collector.
        No parameters are required and no value is returned.

        Returns:
            None
        """
        self.metric_collector.reset()

    def get_codebase_metric_report(self) -> Dict:
        """
        Generates a comprehensive report of codebase metrics.

        This method processes collected data about the codebase and returns a dictionary
        containing various metrics and statistics about the analyzed code.

        Returns:
            Dict: A dictionary containing the following metrics:
                - language_statistics: Computed metrics for each programming language
                - total_files_scanned: Total number of files analyzed
                - total_size_scanned: Total size of all scanned files
                - excluded_directories: List of directories that were excluded from analysis
                - excluded_files: List of files that were excluded from analysis
        """
        collected_data = self.metric_collector.get_collected_data()
        computed_metrics = self.metric_calculator.compute_language_metrics(
            collected_data["language_stats"], collected_data["total_files"]
        )
        return {
            "files": self.list_files_by_Languages(collected_data["language_stats"]),
            "language_statistics": computed_metrics,
            "total_files_scanned": collected_data["total_files"],
            "total_size_scanned": collected_data["total_size"],
            "excluded_directories": collected_data["excluded_dirs"],
            "excluded_files": collected_data["excluded_files"],
        }
