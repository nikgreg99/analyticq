from analyticq.preprocessing.input import CodebaseCloner, CodebaseLangScanner
from analyticq.preprocessing.metric import (CodebaseMetricsCalculator,
                                            CodebaseMetricsCollector,
                                            CodebaseMetricsReporter)
from analyticq.service import GitAuthService
from analyticq.util import BatchUtil, TimeTrackerUtils
from dependency_injector import containers, providers


class UtilContainer(containers.DeclarativeContainer):
    """Container for utilty components."""
    config = providers.Configuration(name='util')

    time_tracker = providers.Singleton(
        TimeTrackerUtils
    )

    batch_util = providers.Factory(
        BatchUtil
    )


class ServiceContainer(containers.DeclarativeContainer):
    """Container for core services."""

    # Configuration for services
    config = providers.Configuration(name='service')

    # Core services
    git_auth_service = providers.Singleton(
        GitAuthService
    )


class InputContainer(containers.DeclarativeContainer):
    """Container for input processing components."""

    # Configuration for input processing
    config = providers.Configuration(name='input')

    git_auth_service = providers.Dependency()
    time_tracker = providers.Dependency()
    metrics_collector = providers.Dependency()
    batch_util = providers.Dependency()

    # Input components
    codebase_cloner = providers.Factory(
        CodebaseCloner,
        git_auth_service=git_auth_service
    )

    codebase_lang_scanner = providers.Factory(
        CodebaseLangScanner,
        time_tracker=time_tracker,
        metrics_collector=metrics_collector
    )


class MetricContainer(containers.DeclarativeContainer):
    """Container for metric related input service"""

    config = providers.Configuration(name="metric")
    metric_calcualtor = providers.Factory(
        CodebaseMetricsCalculator
    )

    metric_collector = providers.Factory(
        CodebaseMetricsCollector
    )

    metric_reporter = providers.Factory(
        CodebaseMetricsReporter,
        metric_calcualtor=metric_calcualtor,
        metric_collector=metric_collector
    )


class PreprocessingContainer(containers.DeclarativeContainer):
    """Container for preprocessing components."""

    # Configuration for preprocessing
    config = providers.Configuration(name='preprocessing')

    # Nested service container
    service = providers.Container(
        ServiceContainer
    )

    util = providers.Container(
        UtilContainer
    )

    metric = providers.Container(
        MetricContainer
    )

    # Input container with properly injected dependencies
    input = providers.Container(
        InputContainer,
        git_auth_service=service.git_auth_service,
        time_tracker=util.time_tracker,
        metrics_collector=metric.metric_collector,
        batch_util=util.batch_util
    )


class AnalyticQContainer(containers.DeclarativeContainer):
    """Root container for the AnalyticQ application."""

    # Main application configuration
    config = providers.Configuration(name='app')

    # Core services container
    service = providers.Container(
        ServiceContainer
    )

    # Util service containers
    util = providers.Container(
        UtilContainer
    )

    # Preprocessing container with its dependencies
    preprocessing = providers.Container(
        PreprocessingContainer
    )
