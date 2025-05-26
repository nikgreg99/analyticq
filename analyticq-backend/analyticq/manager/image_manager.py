import asyncio
import logging
import subprocess
from threading import Lock
from typing import Optional

import aiodocker
from aiodocker.exceptions import DockerError
from analyticq.exception import DockerNotFoundException
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


class DockerRegistryConfig(BaseModel):
    """A configuration class for Docker registry authentication and connection settings.

    This class represents the configuration needed to interact with a Docker registry,
    including optional authentication credentials and registry URL.

    Attributes:
        username (Optional[str]): The username for registry authentication. Defaults to None.
        password (Optional[str]): The password for registry authentication. Defaults to None.
        registry (Optional[str]): The URL of the Docker registry. Must start with 'http://' or 'https://'.
                                Defaults to 'localhost' if None.

    Raises:
        ValueError: If the registry URL is provided but doesn't start with 'http://' or 'https://'.
    """

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

    """Docker Image Manager for handling Docker image operations.

    This class implements the Singleton pattern to manage Docker images, providing
    functionality for checking image existence and pulling images from registries.
    It uses aiodocker for asynchronous Docker operations.

    Attributes:
        docker (aiodocker.Docker): Docker client instance for container operations.
        auth_config (dict): Authentication configuration for Docker registry.
        _initialized (bool): Flag indicating if the instance has been initialized.
        _instance (DockerImageManager): Singleton instance of the class.
        _lock (Lock): Thread lock for ensuring thread-safe singleton instantiation.

        >>> docker_client = aiodocker.Docker()
        >>> image_manager = DockerImageManager(docker_client)
        >>> await image_manager.exists("nginx")
        True
        >>> await image_manager.pull("nginx", "latest")

    Note:
        This class implements the Singleton pattern, ensuring only one instance
        exists throughout the application lifecycle.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, docker_client: aiodocker.Docker):
        self.docker = aiodocker.Docker() if docker_client is None else docker_client
        self.auth_config = None
        self._initialized = True

    @staticmethod
    async def check_docker_availability():
        """
        Check if Docker is available on the system.
        This method verifies if Docker is installed and accessible by attempting to execute
        the 'docker --version' command asynchronously.
        Returns:
        bool: True if Docker is available and running properly.
        Raises:
        DockerNotFoundException: If Docker is not installed or not accessible on the system.
        Example:
            >>> await image_manager.check_docker_availability()
        True
    """
        try:
            process = await asyncio.to_thread(
                subprocess.run,
                ["docker", "--version"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            if process.returncode != 0:
                logger.error("Docker is not available")
                raise DockerNotFoundException("Doker is not availalbe on the system")
            else:
                return True

        except FileNotFoundError:
            raise DockerNotFoundException("Docker is not avaialble on  the system")

    async def login(self, docker_config: DockerRegistryConfig) -> bool:
        """
        Authenticates with a Docker registry using provided credentials.

        This method attempts to log in to a Docker registry using the specified configuration.
        If successful, it stores the authentication configuration for future use.

        Args:
            docker_config (DockerRegistryConfig): Configuration object containing registry credentials
                with the following attributes:
                - registry: URL of the Docker registry
                - username: Username for authentication
                - password: Password for authentication

        Returns:
            None

        Raises:
            No exceptions are raised as they are caught and logged internally

        Example:
            >>> config = DockerRegistryConfig(
            ...     registry="registry.example.com",
            ...     username="user",
            ...     password="pass"
            ... )
            >>> await image_manager.login(config)
        """
        if not docker_config.username or not docker_config.password:
            logger.error("Login failed: Username and password are required")
            return False

        self.auth_config = {
            "username": docker_config.username,
            "password": docker_config.password,
            "serveraddress": docker_config.registry
        }

        try:
            # Since aiodcker doesn't provide a direct access to logout function, a implemantion was the better choice
            process = await asyncio.to_thread(
                subprocess.run,
                ["docker", "login", docker_config.registry, "--username" , docker_config.username, "--password", docker_config.password],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            if process.returncode != 0:
                logger.error(f"Failed to log in to registry {docker_config.registry}: {process.stderr.decode()}")
                self.auth_config = None
                return False

            logger.info(f"Successfully logged in to registry: {docker_config.registry}")
            return True

        except Exception:
            self.auth_config = None
            logger.error("Error during login:")
            return False

    async def logout(self) -> None:
        """
        Logs out from the Docker registry using the stored authentication configuration.

        This method performs a Docker logout operation using the stored server address from auth_config.
        It clears the authentication configuration after successful logout.

        Returns:
            None

        Raises:
            RuntimeError: If no prior login was performed (auth_config is None)
            Exception: If the logout operation fails for any other reason

        Notes:
            - Uses subprocess.run since aiodocker doesn't provide direct logout functionality
            - Clears auth_config after successful logout for security
            - Logs the operation status using the logger
        """

        if self.auth_config is None:
            logger.warning("Docker logout could not be executed, because no login to registry has been done before")
            raise RuntimeError("No login has been performed yet")

        server_address = self.auth_config["serveraddress"]

        try:
            # Since aiodcker doesn't provide a direct access to logout function, a implemantion was the better choice
            process = await asyncio.to_thread(
                subprocess.run,
                ["docker", "logout", server_address],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Store auth_config reference before clearing it for logging purposes
            temp_server = server_address
            self.auth_config = None

            if process.returncode != 0:
                error_msg = process.stderr.decode()
                logger.warning(f"Failed to log out from registry {temp_server}: {error_msg}")
                return False

            logger.info(f"Successfully logged out from registry {temp_server}")
            return True

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            # Clear auth config even if logout fails
            self.auth_config = None
            raise

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
        if not image_name:
            logger.error("Cannot check existence of image with empty name")
            return False

        try:
            await self.docker.images.get(f"{image_name}:{image_tag}")
            return True
        except DockerError:
            return False

    async def pull(self, image_name: str, image_tag: str, registry_url: str = None) -> bool:
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
        if image_name is None or image_tag is None:
            raise ValueError("Image name and tag cannot be None or empty.")
        try:
            full_image_name = f"{registry_url}/{image_name}" if registry_url else image_name

            await self.docker.images.pull(full_image_name, tag=image_tag, auth=self.auth_config)
            logger.info(f"Successfully pulled {image_name}:{image_tag}")
            return True
        except DockerError as e:
            logger.warning(f"Failed to pull image {image_name}:{image_tag}: {str(e)}")
            # Check if the image exists locally
            if await self.exists(image_name, image_tag):
                logger.info(f"Using locally available image {image_name}:{image_tag}")
                return True
            else:
                logger.error(f"Image {image_name}:{image_tag} not found locally or in the registry")
                return False

    async def close(self):
        """
        Closes the Docker client connection if it exists.

        This method ensures proper cleanup of Docker resources by closing the Docker client
        connection when the manager is being shut down.

        Returns:
            None

        Raises:
            None
        """
        if hasattr(self, 'docker') and self.docker:
            await self.docker.close()
            logger.info("Docker client connection closed")
