from typing import Dict


class CodebaseMetricsCalculator:

    @staticmethod
    def _average_size(data: Dict):
        return data["total_size"] / data["count"] if data["count"] > 0 else 0

    @staticmethod
    def _percentage_files(data: Dict, total_files: int):
        return (data["count"] / total_files) * 100 if total_files > 0 else 0

    @staticmethod
    def compute_language_metrics(language_stats: Dict[str, Dict], total_files: int) -> Dict:
        """Computes derived statistics for each language."""
        return {
            lang: {
                "file_count": data["count"],
                "total_size": data["total_size"],
                "largest_file": data["largest_file"],
                "smallest_file": data["smallest_file"],
                "average_size": CodebaseMetricsCalculator._average_size(data),
                "percentage_files": CodebaseMetricsCalculator._percentage_files(data, total_files)
            }
            for lang, data in language_stats.items()
        }
