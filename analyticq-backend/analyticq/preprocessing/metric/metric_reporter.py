from typing import Dict

from .metric_calculator import CodebaseMetricsCalculator
from .metric_collector import CodebaseMetricsCollector


class CodebaseMetricsReporter:

    def __init__(self, collector: CodebaseMetricsCollector, calculator: CodebaseMetricsCalculator):
        self.collector = collector
        self.calculator = calculator

    def get_codebase_metric_report(self) -> Dict:
        collected_data = self.collector.get__collected_data()
        computed_metrics = self.calculator.compute_language_metrics(
            collected_data["language_stats"], collected_data["total_files"]
        )

        return {
            "language_statistics": computed_metrics,
            "total_files_scanned": collected_data["total_files"],
            "total_size_scanned": collected_data["total_size"],
            "excluded_directories": collected_data["excluded_dirs"],
            "excluded_files": collected_data["excluded_files"],
        }
