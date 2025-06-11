import asyncio
import logging
import os
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional

import aiodocker
from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)

from .image_manager import DockerImageManager

logger = logging.getLogger(__name__)


class AnalyticQContainerLogger:
    @staticmethod
    async def stream_logs(container: aiodocker.containers.DockerContainer, container_id: str) -> AsyncIterator[str]:
        logs = container.log(stdout=True, stderr=True, follow=True)
        while True:
            try:
                log_line = await anext(logs)
                if log_line:
                    log_line = log_line.strip()
                    logger.info(f"Container {container_id} output: {log_line}")
                    yield log_line
            except StopAsyncIteration:
                break
            except Exception as e:
                logger.error(f"Error reading log line: {str(e)}")
                break


class AnalyticQContainerManager:

    def __init__(
        self,
        runtime_config: AnalyticQContainerRuntimeConfig = AnalyticQContainerRuntimeConfig()
    ):
        self.docker = None
        self.runtime_config = runtime_config
        self.initialized = False
        self._cleanup_lock = asyncio.Lock()

    async def initialize(self):
        """
        Initialize the Docker client asynchronously.
        This method should be called explicitly to initialize the class.
        """
        if not self.initialized:
            try:
                docker_host = os.getenv('DOCKER_HOST', '')
                if docker_host.startswith("tcp://"):
                    self.docker = aiodocker.Docker(url=docker_host)
                else:
                    self.docker = aiodocker.Docker()
                await self.docker.version()
                self.initialized = True
                self.image_manager = DockerImageManager(self.docker)
            except Exception as e:
                logger.error(f"Failed to initialize Docker client: {e}")
                await self.cleanup()
                raise

    async def cleanup(self):
        """
        Cleanup the Docker client connection and reset initialization state.

        Returns:
            None
        """
        async with self._cleanup_lock:
            if self.docker is not None:
                try:
                    await self.docker.close()
                except Exception as e:
                    logger.error(f"Error during Docker client cleanup: {e}")
                finally:
                    self.docker = None
                    self.image_manager = None
                    self.initialized = False

    async def __aenter__(self):
        """
        Async context manager entry method.

        This method is called when entering an async context manager using the 'async with' statement.
        It returns the instance of the class itself, allowing it to be used within the context.

        Returns:
            self:
             Returns the instance of the class to be used within the context manager.
        """
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Asynchronous context manager exit method that closes the Docker client connection.

        Args:
            exc_type: The type of the exception that was raised, if any
            exc_val: The instance of the exception that was raised, if any
            exc_tb: The traceback of the exception that was raised, if any

        Returns:
            None
        """
        await self.cleanup()

    async def _image_exists(self, image_name: str, image_tag: str = "latest") -> bool:
        """
        Check if a Docker image exists in the local registry.

        Args:
            image_name (str): Name of the Docker image to check.
            image_tag (str, optional): Tag of the Docker image. Defaults to "latest".

        Returns:
            bool: True if the image exists, False otherwise.
        """
        is_existing_image = await self.image_manager.exists(image_name, image_tag)
        return is_existing_image

    async def pull_image(self, image_name: str, image_tag: str) -> None:
        """
        Pull a Docker image asynchronously from a registry.

        This method delegates the image pulling operation to the image manager.

        Args:
            image_name (str): Name of the Docker image to pull
            image_tag (str): Tag of the Docker image version to pull

        Returns:
            None: This method doesn't return anything but triggers image pull

        Raises:
            DockerException: If there is an error while pulling the image
        """
        return self.image_manager.pull(image_name, image_tag)

    async def _prepare_container_config(
        self,
        full_image: str,
        container_id: str,
        command_args: List[str],
        volumes: Dict[Path, Dict[str, str]],
        env_vars: Optional[Dict[str, str]]
    ) -> Dict:
        """
        Prepare container configuration with proper volume validation.
        """
        # Validate volume paths
        for host_path in volumes:
            if not host_path.exists():
                raise ScanConfigurationException(
                    f"Invalid host path: {host_path} does not exist"
                )

        volumes_config = {
            str(host_path): {
                "bind": mount_options["bind"],
                "mode": mount_options.get("mode", "ro")
            }
            for host_path, mount_options in volumes.items()
        }

        network_mode = self.runtime_config.network.mode
        network_disabled = network_mode == "none"

        config = {
            "Image": full_image,
            "Cmd": command_args,
            "Env": [f"{k}={v}" for k, v in (env_vars or {}).items()],
            "HostConfig": {
                "Binds": [f"{h}:{c['bind']}:{c['mode']}" for h, c in volumes_config.items()],
                "NetworkMode": "none" if network_disabled else network_mode,
                "CpuShares": self.runtime_config.cpu_shares,
                "ReadonlyRootfs": self.runtime_config.read_only,
                "SecurityOpt": self.runtime_config.security_opts,
            },
            "Name": f"analyticq-scan-{container_id}",
        }

        logger.debug(f"Container configuration: {config}")
        return config

    async def run_container_command(
        self,
        image_name: str,
        image_tag: str = "latest",
        command_args: List[str] = None,
        volumes: Dict[Path, Dict[str, str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        file_path: str = ""
    ):
        """
        Run a container command asynchronously.

        Args:
            image_name (str): The name of the Docker image
            image_tag (str): The tag of the Docker image
            command_args (List[str]): Command arguments to run in the container
            volumes (Dict[Path, Dict[str, str]]): Volume mappings
            env_vars (Dict[str, str], optional): Environment variables
            timeout (int, optional): Command timeout in seconds


        Raises:
            ScanConfigurationException: If configuration is invalid
            RuntimeError: If container execution fails
        """
        if not self.initialized:
            raise RuntimeError("Container manager not initialized")

        full_image = f"{image_name}:{image_tag}"
        container_id = os.urandom(8).hex()
        container = None

        try:
            # Container configuration
            config = await self._prepare_container_config(
                full_image, container_id, command_args or [],
                volumes or {}, env_vars
            )

            # Create and run container
            container = await self.docker.containers.create(config=config)

            await container.start()
            logger.info(f"Container {container_id} started")

            async for _ in AnalyticQContainerLogger.stream_logs(container, container_id):
                pass

            result = await container.wait()

            if result["StatusCode"] != 0:
                raise RuntimeError(f"Container exited with code {result['StatusCode']}")

            if file_path:
                output_path = list(volumes.keys())[-1]
                if output_path.exists():
                    return (output_path / file_path).read_text()
                return None

        except asyncio.TimeoutError as e:
            raise ScanTimeoutException(f"{str(e)}") from e
        except Exception as e:
            raise ScanConfigurationException(f"Docker API error: {str(e)}") from e
        finally:
            if container:
                try:
                    await container.delete(force=True)
                except Exception as e:
                    logger.warning(f"Failed to delete container {container_id}: {e}")
