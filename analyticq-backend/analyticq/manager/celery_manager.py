import logging
from threading import Lock
from typing import Optional

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
        return cls._instance

    def __init__(self, settings: Optional[AnalyticQCeleryConfig] = None):
        if not hasattr(self, "_initialized"):
            self.settings = settings or AnalyticQCeleryConfig()
            # Create the Celery application
            self.celery = Celery(
                "analyticq",
                broker=self.settings.broker_url,
                backend=self.settings.result_backend,
            )
            self.configure_app()
            self._intizialized = True

    def configure_app(self) -> None:
        """
        Configure the Celery application with settings and tasks.
        This method performs the following configurations:
        1. Updates Celery configuration from settings (excluding autodiscover_tasks and beat_schedule)
        2. Autodiscovers tasks from specified packages if autodiscover_tasks is configured
        3. Updates the beat schedule with CELERY_BEAT configuration
        """
        celery_conf_dict = self.settings.model_dump(exclude=["autodiscover_tasks", "beat_schedule"])
        self.celery.conf.update(celery_conf_dict)

        # Handling autodiscover tasks
        autodiscover_tasks = self.settings.get_autodiscover_tasks()
        if autodiscover_tasks:
            self.celery.autodiscover_tasks(autodiscover_tasks, force=True)

        self.celery.conf.update(beat_schedule=CELERY_BEAT)

    def get_celery_app(self) -> Celery:
        return self.celery

    @classmethod
    def reset(cls):
        """
        Reset the singleton instance, useful for testing or dynamic reconfiguration.
        """
        with cls._lock:
            cls._instance = None
