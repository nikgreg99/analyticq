import logging
from threading import Lock
from typing import Any, Dict, Optional

from analyticq.config.models import AnalyticQCeleryConfig
from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)


CELERY_BEAT = {
    "cleanup_old_codebase":
    {
        "task": "analyticq.tasks.cleanup.cleanup_old_codebase",
        "schedule": crontab(minute="*/10")
    }
}


class AnalyticQCeleryManager:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, settings: Optional[AnalyticQCeleryConfig] = None):
        with self._lock:
            if not self._initialized:
                self.settings = settings or AnalyticQCeleryConfig()
                logger.info("Initializing AnalyticQCeleryManager")
                try:
                    # Create the Celery application
                    self.celery = Celery(
                        "analyticq",
                        broker=self.settings.broker_url,
                        backend=self.settings.result_backend,
                    )
                    self.configure_app()
                    self._initialized = True
                    logger.info("AnalyticQCeleryManager initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize AnalyticQCeleryManager: {str(e)}")
                    raise

    def configure_app(self) -> None:
        try:
            # Get celery configuration from settings, excluding special fields
            celery_conf_dict = self.settings.model_dump(
                exclude=["autodiscover_tasks", "beat_schedule"]
            )

            # Update Celery configuration
            self.celery.conf.update(celery_conf_dict)

            # Handling autodiscover tasks
            autodiscover_tasks = self.settings.get_autodiscover_tasks()
            if autodiscover_tasks:
                logger.debug(f"Autodiscovering tasks from: {autodiscover_tasks}")
                self.celery.autodiscover_tasks(autodiscover_tasks, force=True)

            # Merge default beat schedule with any provided in settings
            beat_schedule = dict(CELERY_BEAT)
            if hasattr(self.settings, 'beat_schedule') and self.settings.beat_schedule:
                beat_schedule.update(self.settings.beat_schedule)

            # Update beat schedule
            self.celery.conf.update(beat_schedule=beat_schedule)
            logger.info("Celery application successfully configured")

        except Exception as e:
            logger.error(f"Failed to configure Celery application: {str(e)}")
            raise

    def health_check(self) -> bool:
        """
        Performs a health check on the Celery worker system.

        This method pings all Celery workers and verifies that at least one worker responds
        within the timeout period.

        Returns:
            bool: True if the Celery infrastructure is healthy, False otherwises
        """
        try:
            ping = self.celery.control.ping(timeout=1.0)
            result = len(ping) > 0
            if result:
                logger.debug("Celery health check successful")
            else:
                logger.warning("Celery health check failed: No workers responded")
        except Exception as e:
            logger.error(f"Celery health check failed: {str(e)}")
            return False

    def get_worker_status(self) -> Optional[Dict[str, Any]]:
        """
        Get the status of Celery workers.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the active worker status information,
            where keys are worker names and values are their current tasks.
            Returns None if there was an error retrieving the status.
        """
        try:
            status = self.celery.control.inspect().active()
            logger.debug(f"Worker status retrieved: {len(status) if status else 0} workers found")
            return status
        except Exception as e:
            logger.error(f"Failed to get worker status: {str(e)}")
            return None

    def get_celery_app(self) -> Celery:
        """
        Returns the Celery application instance.

        Returns:
            Celery: The Celery application instance managed by this class.
        """
        return self.celery

    def __enter__(self):
        """
        Context manager enter method that returns the instance itself.

        Returns:
            self: The instance of the class implementing the context manager protocol
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        A context manager exit method that cleans up resources.

        This method is called when exiting the context manager block, regardless of whether
        an exception occurred or not.

        Args:
            exc_type: The type of the exception that was raised, if any
            exc_val: The instance of the exception that was raised, if any
            exc_tb: The traceback of the exception that was raised, if any

        Returns:
            None
        """
        pass

    @classmethod
    def reset(cls):
        """
        Reset the singleton instance.

        """
        with cls._lock:
            if cls._instance is not None:
                logger.info("Resetting AnalyticQCeleryManager instance")
                cls._instance = None
