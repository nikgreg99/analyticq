import statistics
from typing import Dict, List


class CodebaseMetricsCalculator:

    @staticmethod
    def _average_size(data: Dict) -> float:
        """Calculate the average size from the provided data dictionary.

        Args:
            data (Dict): Dictionary containing 'total_size' and 'count' keys with numeric values

        Returns:
            float: Average size calculated as total_size/count if count > 0, otherwise returns 0

        Example:
            >>> data = {'total_size': 100, 'count': 4}
            >>> _average_size(data)
            25.0
        """
        return data["total_size"] / data["count"] if data["count"] > 0 else 0

    @staticmethod
    def _percentage_files(data: Dict, total_files: int) -> int:
        """
        Calculate the percentage of files relative to the total number of files.

        Args:
            data (Dict): Dictionary containing count of files
            total_files (int): Total number of files

        Returns:
            int: Percentage of files (0-100). Returns 0 if total_files is 0.
        """
        return (data["count"] / total_files) * 100 if total_files > 0 else 0

    @staticmethod
    def _median_size(file_sizes: List[int]) -> float:
        """
        Calculate the median size from a list of file sizes.

        Args:
            file_sizes (List[int]): A list of file sizes in bytes.

        Returns:
            float: The median size of files. Returns 0 if the input list is empty.
        """
        return statistics.median(file_sizes) if file_sizes else 0

    @staticmethod
    def _standard_deviation(file_sizes: List[int]) -> float:
        """
        Calculate the standard deviation of file sizes.

        Measures the dispersion or variability of file sizes from their mean value.
        Returns 0 if there is only one file size provided.

        Args:
            file_sizes (List[int]): List of file sizes in bytes

        Returns:
            float: Standard deviation of file sizes. Returns 0 if list contains less than 2 elements
        """
        return statistics.stdev(file_sizes) if len(file_sizes) > 1 else 0

    @staticmethod
    def compute_language_metrics(language_stats: Dict[str, Dict], total_files: int) -> Dict:
        """
        Calculate various metrics for each programming language in the codebase.
        Args:
            language_stats (Dict[str, Dict]): Dictionary containing statistics for each language.
                Expected format:
                {
                    "language_name": {
                        "count": int,  # Number of files
                        "total_size": int,  # Total size in bytes
                        "largest_file": int,  # Size of largest file in bytes
                        "smallest_file": int  # Size of smallest file in bytes
            total_files (int): Total number of files in the codebase
        Returns:
            Dict: Dictionary containing computed metrics for each language.
        """
        return {
            lang: {
                "file_count": data["count"],
                "total_size": data["total_size"],
                "largest_file": data["largest_file"],
                "smallest_file": data["smallest_file"],
                "average_size": CodebaseMetricsCalculator._average_size(data),
                "median_size": CodebaseMetricsCalculator._median_size(data.get("file_sizes", [])),
                "std_size": CodebaseMetricsCalculator._standard_deviation(data.get("file_sizes", [])),
                "percentage_files": CodebaseMetricsCalculator._percentage_files(data, total_files),
            }
            for lang, data in language_stats.items()
        }
