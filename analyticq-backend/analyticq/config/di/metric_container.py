from analyticq.preprocessing import (CodebaseMetricsCalculator,
                                     CodebaseMetricsCollector,
                                     CodebaseMetricsReporter)
from dependency_injector import containers, providers


class MetricContainer(containers.DeclarativeContainer):
    """Container for metric-related services."""

    metrics_calculator = providers.Singleton(CodebaseMetricsCalculator)
    metric_collector = providers.Factory(CodebaseMetricsCollector)
    metric_reporter = providers.Factory(
        CodebaseMetricsReporter,
        collector=metric_collector,
        calculator=metrics_calculator
    )
