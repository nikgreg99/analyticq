import base64
import logging
from threading import Lock
from typing import Optional

import aiodocker
from aiodocker.exceptions import DockerError
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


class DockerRegistryConfig(BaseModel):

    username: Optional[str] = None
    password: Optional[str] = None
    registry: Optional[str] = None

    @field_validator("registry")
    @classmethod
    def validate_registry_url(cls, v):
        if v is None:
            return "localhost"
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("registry_url must start with 'http://' or 'https://'")
        return v


class DockerImageManager:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, docker_client: aiodocker):
        self.docker = docker_client
        self.auth_config = None
        self._initialized = True

    def _init_auth_config(self):
        docker_config = DockerRegistryConfig(username="", password="", registry="")
        return {
            "serveradrress": docker_config.registry,
            "auth": self._encode_auth(docker_config.username, docker_config.password)
        }

    def _encode_auth(self, username: str, password: str) -> str:
        """
        Encode authentication credentials using base64 encoding.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            str: Base64 encoded string of 'username:password' credentials.

        Example:
            >>> _encode_auth("user", "pass")
            'dXNlcjpwYXNz'
        """
        auth_string = f"{username}:{password}"
        return base64.b64encode(auth_string.encode()).decode()

    async def exists(self, image_name: str, image_tag: str = "latest") -> bool:
        """Check if a Docker image exists locally.

        This method checks if a Docker image with the specified name and tag exists in the local Docker registry.

        Args:
            image_name (str): Name of the Docker image to check
            image_tag (str, optional): Tag of the Docker image. Defaults to "latest"

        Returns:
            bool: True if the image exists locally, False otherwise

        Raises:
            None: Any DockerError exceptions are caught and return False
        """
        try:
            await self.docker.images.get(f"{image_name}:{image_tag}")
            return True
        except DockerError:
            return False

    async def pull(self, image_name: str, image_tag: str, registry_url: str = None) -> None:
        """
        Pull a Docker image from a registry.
        This method pulls a Docker image with the specified name and tag from a Docker registry.
        Args:
            image_name (str): The name of the image to pull.
            image_tag (str): The tag of the image to pull.
            registry_url (str); the registry if the image is located into a private docker registry.
        Raises:
            TypeError: If image_name or image_tag is None.
            RuntimeError: If the image pull operation fails.
        Returns:
            None: This method doesn't return anything.
        """
        try:
            if image_name is None or image_tag is None:
                raise ValueError("Image name and tag cannot be None or empty.")

            full_image_name = f"{registry_url}/{image_name}" if registry_url else image_name

            await self.docker.images.pull(full_image_name, tag=image_tag, auth=self.auth_config)
            logger.info(f"Successfully pulled {image_name}:{image_tag}")
        except DockerError as e:
            raise RuntimeError(f"Failed to pull image {image_name}:{image_tag}: {str(e)}")
