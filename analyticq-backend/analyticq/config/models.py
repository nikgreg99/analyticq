import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from analyticq.util import FileUtil
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class AnalyticQCeleryConfig(BaseSettings):

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

    broker_connection_retry_on_setup: bool = Field(
        default_factory=lambda: os.environ.get('CELERY_BROKER_CONNECTION_RETRY_ON_SETUP', 'true').lower() == 'true'
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
        """
        Validates the Celery broker URL.

        Args:
            v (str): The broker URL to validate.

        Returns:
            str: The validated broker URL.

        Raises:
            ValueError: If the broker URL is empty or None.

        Example:
            >>> validate_broker_url("amqp://guest:guest@localhost:5672//")
            'amqp://guest:guest@localhost:5672//'
        """
        if not v:
            raise ValueError("CELERY_BROKER_URL must be set")
        return v

    @field_validator('result_backend')
    def validate_result_backend(cls, v: str) -> str:
        """
        Validates the Celery result backend configuration.

        This method ensures that a result backend URL is provided for Celery configuration.
        The result backend is required for storing and retrieving task results.

        Args:
            cls: The class instance
            v (str): The result backend URL string to validate

        Returns:
            str: The validated result backend URL

        Raises:
            ValueError: If the result backend URL is empty or None
        """
        if not v:
            raise ValueError("CELERY_RESULT_BACKEND must be set")
        return v

    def get_autodiscover_tasks(self) -> List[str]:
        """
        Retrieve the list of tasks to be autodiscovered by Celery.

        This method processes the autodiscover_tasks attribute and returns a list of task names.
        It handles three different input formats:
        - A Python list
        - A JSON string that can be parsed into a list
        - A comma-separated string

        Returns:
            List[str]: A list of task names to be autodiscovered.
                - If input is already a list, returns it as is
                - If input is valid JSON that converts to a list, returns the parsed list
                - If input is a string, splits by comma and returns non-empty stripped items
        """
        if isinstance(self.autodiscover_tasks, list):
            return self.autodiscover_tasks
        try:
            tasks_list = json.loads(self.autodiscover_tasks)
            if isinstance(tasks_list, list):
                return tasks_list
        except json.JSONDecodeError:
            logger.error("Error parsing Celery Config")
            raise
        return [item.strip() for item in self.autodiscover_tasks.split(",") if item.strip()]

    def get_beat_schedule(self) -> Dict[str, Dict[str, Any]]:
        """Returns the Celery beat schedule configuration.

        The beat schedule defines periodic tasks that should be executed by Celery workers
        at specified intervals.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary containing the beat schedule configuration,
            where each key is a task name and the value is a dictionary with task settings
            like schedule interval, task function, and arguments.
        """
        return self.beat_schedule


class AnalyticQContainerNetworkConfig(BaseModel):
    """Container network configuration settings for docker containers.

    This model defines the network configuration options for docker containers, including
    network mode, internet access, DNS settings and port mappings.

    Attributes:
        mode (str): Network mode for the container. Valid values are:
            - "none": No networking
            - "bridge": Default bridge network
            - "host": Host networking
            - "overlay": Overlay networking for swarm services
            - "macvlan": MAC VLAN networking
            Defaults to "none".

        allow_outbound (bool): Whether to allow outbound internet access from the container.
            Defaults to False.

        dns_servers (List[str], optional): List of DNS server IP addresses to use.
            Defaults to None.

        ports (Dict[str, str], optional): Port mapping configuration as host:container pairs.
            For example: {"8080": "80"} maps host port 8080 to container port 80.
            Defaults to None.
    """
    mode: str = "none"  # none, bridge, host, overlay, macvlan
    allow_outbound: bool = False  # Allow outbound internet access
    dns_servers: Optional[List[str]] = None
    ports: Optional[Dict[str, str]] = None  # Port mappings (host:container)


class AnalyticQContainerRuntimeConfig(BaseModel):
    """Configuration settings for container runtime environment.
    This class defines the runtime configuration parameters for containerized execution.
    Attributes:
        name (str): Container runtime name (default: "docker")
        timeout (int): Maximum execution time in seconds (default: 600)
        memory (str): Memory limit for the container (default: "1g")
        network (ContainerNetworkConfig): Network configuration settings
        user (str): User and group to run container as (default: "nobody:nogroup")
        read_only (bool): Whether to mount container filesystem as read-only (default: True)
        security_opts (List[str]): Security options for container (default: ["no-new-privileges:true"])
    """

    name: str = "docker"
    timeout: int = 600
    memory: str = "1g"
    cpu_shares: int = 512
    network: AnalyticQContainerNetworkConfig = AnalyticQContainerNetworkConfig()
    user: str = "nobody:nogroup"
    read_only: bool = False
    security_opts: List[str] = ["no-new-privileges:true"]
