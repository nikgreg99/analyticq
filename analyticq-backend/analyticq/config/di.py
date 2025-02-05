from analyticq.preprocessing.input import (CodebaseCleaner, CodebaseCloner,
                                           CodebaseLangScanner,
                                           CodebasePreprocessor)
from analyticq.preprocessing.metric import (CodebaseMetricsCalculator,
                                            CodebaseMetricsCollector,
                                            CodebaseMetricsReporter)
from analyticq.service import GitAuthService
from analyticq.util import BatchUtil, TimeTrackerUtils
from dependency_injector import containers, providers


class UtilContainer(containers.DeclarativeContainer):
    """Container for utility components."""

    config = providers.Configuration(name="util")

    time_tracker = providers.Singleton(TimeTrackerUtils)
    batch_util = providers.Factory(BatchUtil)


class ServiceContainer(containers.DeclarativeContainer):
    """Container for core services."""

    config = providers.Configuration(name="service")

    git_auth_service = providers.Singleton(GitAuthService)


class MetricContainer(containers.DeclarativeContainer):
    """Container for metric-related components."""

    config = providers.Configuration(name="metric")

    metric_calculator = providers.Factory(CodebaseMetricsCalculator)
    metric_collector = providers.Factory(CodebaseMetricsCollector)

    metric_reporter = providers.Factory(
        CodebaseMetricsReporter,
        metric_calculator=metric_calculator,
        metric_collector=metric_collector
    )


class InputContainer(containers.DeclarativeContainer):
    """Container for input processing components."""

    config = providers.Configuration(name="input")

    # Dependencies provided externally
    git_auth_service = providers.Dependency()
    time_tracker = providers.Dependency()
    metrics_reporter = providers.Dependency()
    batch_util = providers.Dependency()

    codebase_cloner = providers.Factory(
        CodebaseCloner,
        git_auth_service=git_auth_service
    )

    codebase_cleaner = providers.Singleton(CodebaseCleaner)

    codebase_lang_scanner = providers.Factory(
        CodebaseLangScanner,
        time_tracker=time_tracker,
        metrics_reporter=metrics_reporter,
        batch_util=batch_util
    )

    codebase_preprocessor = providers.Singleton(
        CodebasePreprocessor,
        cloner=codebase_cloner,
        lang_scan=codebase_lang_scanner
    )


class AnalyticQContainer(containers.DeclarativeContainer):
    """Root container for the AnalyticQ application."""

    config = providers.Configuration(name="app")

    # Core containers
    util = providers.Container(UtilContainer)
    service = providers.Container(ServiceContainer)
    metric = providers.Container(MetricContainer)

    # Input container with injected dependencies
    input = providers.Container(
        InputContainer,
        git_auth_service=service.git_auth_service,
        time_tracker=util.time_tracker,
        metrics_reporter=metric.metric_reporter,
        batch_util=util.batch_util
    )
