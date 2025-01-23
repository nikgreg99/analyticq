from analyticq.preprocessing import CodebaseLangScanner
from analyticq.util import TimeTrackerUtils
from dependency_injector import containers, providers

from .metric_container import MetricContainer
from .util_container import UtilContainer


class InputContainer(containers.DeclarativeContainer):
    """Container for input-related services."""

    time_tracker_provider = providers.Factory(TimeTrackerUtils)

    util_container = providers.Container(UtilContainer)
    metric_container = providers.Container(MetricContainer)

    input_codebase_scanner = providers(
        CodebaseLangScanner,
        metric_collector=metric_container.container.metric_collector,
        time_tracker=time_tracker_provider
    )
