from dependency_injector import containers, providers

from .input_container import InputContainer
from .metric_container import MetricContainer
from .util_container import UtilContainer


class PreprocessingContainer(containers.DeclarativeContainer):
    """Container for preprocessing-related services."""

    util_container = providers.Container(UtilContainer)

    metrics_container = providers.Container(MetricContainer)
    codebase_lang_scanner = providers.Container(
        InputContainer,
        metric_container=metrics_container,
        time_tracker=util_container.container.time_tracker_service
    )
