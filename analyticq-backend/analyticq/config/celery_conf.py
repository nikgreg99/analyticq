import json
import logging
import os
from threading import Lock
from typing import Any, Dict, List, Optional, Union

from analyticq.util import FileUtil
from celery import Celery
from celery.schedules import crontab
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


CELERY_BEAT = {
    "cleanup_old_codebase":
    {
        "task": "analyticq.tasks.cleanup.cleanup_old_codebase",
        "schedule": crontab(minute="*/10")
    }
}


class CelerySettings(BaseSettings):

    hostname: str = Field(default_factory=lambda: os.environ.get("CELERY_HOSTNAME", "localhost"))
    broker_url: str = Field(default_factory=lambda: os.environ.get('CELERY_BROKER_URL', ''))
    result_backend: str = Field(default_factory=lambda: os.environ.get('CELERY_RESULT_BACKEND', ''))

    task_serializer: str = Field(default_factory=lambda: os.environ.get('CELERY_TASK_SERIALIZER', 'json'))

    result_serializer: str = Field(
        default_factory=lambda: os.environ.get("CELERY_RESULT_SERIALIZER", "json")
    )
    accept_content: List[str] = Field(default_factory=lambda: json.loads(
        os.environ.get('CELERY_ACCEPT_CONTENT', '["json"]')
    ))

    timezone: str = Field(
        default_factory=lambda: os.environ.get('CELERY_TIMEZONE', 'UTC')
    )

    enable_utc: bool = Field(
        default_factory=lambda: os.environ.get('CELERY_ENABLE_UTC', 'true').lower() == 'true'
    )

    autodiscover_tasks: Union[List[str], str] = Field(default_factory=lambda: FileUtil.parse_list_env('CELERY_AUTODISCOVER_TASKS', []))

    beat_schedule: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict
    )

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        env_prefix="CELERY_",
        extra="ignore",
        validate_assignment=True
    )

    @field_validator('broker_url')
    def validate_broker_url(cls, v: str) -> str:
        if not v:
            raise ValueError("CELERY_BROKER_URL must be set")
        return v

    @field_validator('result_backend')
    def validate_result_backend(cls, v: str) -> str:
        if not v:
            raise ValueError("CELERY_RESULT_BACKEND must be set")
        return v

    def get_autodiscover_tasks(self) -> List[str]:
        if isinstance(self.autodiscover_tasks, list):
            return self.autodiscover_tasks
        try:
            tasks_list = json.loads(self.autodiscover_tasks)
            if isinstance(tasks_list, list):
                return tasks_list
        except json.JSONDecodeError:
            pass
        return [item.strip() for item in self.autodiscover_tasks.split(",") if item.strip()]

    def get_beat_schedule(self) -> Dict[str, Dict[str, Any]]:
        return self.beat_schedule


class CeleryConf:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: Optional[CelerySettings] = None):
        if not hasattr("initialized"):
            self.settings = settings or CelerySettings()
            # Create the Celery application
            self.celery = Celery(
                "analyticq",
                broker=self.settings.broker_url,
                backend=self.settings.result_backend,
            )
            self.configure_app()
            self.intizialized = True

    def configure_app(self) -> None:
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
