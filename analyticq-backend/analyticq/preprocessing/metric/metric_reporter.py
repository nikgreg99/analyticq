from typing import Dict

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

    def get_codebase_metric_report(self) -> Dict:
        collected_data = self.metric_collector.get_collected_data()
        computed_metrics = self.metric_calculator.compute_language_metrics(
            collected_data["language_stats"], collected_data["total_files"]
        )

        return {
            "language_statistics": computed_metrics,
            "total_files_scanned": collected_data["total_files"],
            "total_size_scanned": collected_data["total_size"],
            "excluded_directories": collected_data["excluded_dirs"],
            "excluded_files": collected_data["excluded_files"],
        }
