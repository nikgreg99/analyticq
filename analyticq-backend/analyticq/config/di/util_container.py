from analyticq.util import TimeTracker
from dependency_injector import containers, providers


class UtilContainer(containers.DeclarativeContainer):
    """Container for util-related services."""

    time_tracker_service = providers.Factory(TimeTracker)
