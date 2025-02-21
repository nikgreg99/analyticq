import logging

import aiodocker

logger = logging.getLogger(__name__)


class DockerImageManager:
    def __init__(self, docker_client: aiodocker.Docker):
        self.docker = docker_client

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
        except aiodocker.exceptions.DockerError:
            return False

    async def pull(self, image_name: str, image_tag: str) -> None:
        """
        Pull a Docker image from a registry.
        This method pulls a Docker image with the specified name and tag from a Docker registry.
        Args:
            image_name (str): The name of the image to pull.
            image_tag (str): The tag of the image to pull.
        Raises:
            TypeError: If image_name or image_tag is None.
            RuntimeError: If the image pull operation fails.
        Returns:
            None: This method doesn't return anything.
        """
        try:
            if image_name is None or image_tag is None:
                raise TypeError()

            await self.docker.images.pull(image_name, tag=image_tag)
            logger.info(f"Successfully pulled {image_name}:{image_tag}")
        except aiodocker.exceptions.DockerError as e:
            raise RuntimeError(f"Failed to pull image {image_name}:{image_tag}: {str(e)}")
