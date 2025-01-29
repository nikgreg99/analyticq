from analyticq.preprocessing.input import CodebaseCloner
from analyticq.preprocessing.metric import (CodebaseMetricsCalculator,
                                            CodebaseMetricsCollector,
                                            CodebaseMetricsReporter)
from analyticq.service import GitAuthService
from analyticq.util import TimeTrackerUtils
from dependency_injector import containers, providers


class UtilContainer(containers.DeclarativeContainer):
    """Container for utilty components."""
    config = providers.Configuration(name='util')

    time_tracker = providers.Singleton(
        TimeTrackerUtils
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

    # Input components
    codebase_cloner = providers.Factory(
        CodebaseCloner,
        git_auth_service=git_auth_service
    )


class MetricContainer(containers.DeclarativeContainer):

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

    # Input container with properly injected dependencies
    input = providers.Container(
        InputContainer,
        git_auth_service=service.git_auth_service
    )

    metric = providers.Container(
        MetricContainer
    )


class AnalyticQContainer(containers.DeclarativeContainer):
    """Root container for the AnalyticQ application."""

    # Main application configuration
    config = providers.Configuration(name='app')

    # Core services container
    service = providers.Container(
        ServiceContainer
    )

    # Preprocessing container with its dependencies
    preprocessing = providers.Container(
        PreprocessingContainer,
        service=service
    )
