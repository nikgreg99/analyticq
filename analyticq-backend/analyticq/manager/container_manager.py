import logging
import os
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

import aiodocker
from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.exception import ScanConfigurationException

logger = logging.getLogger(__name__)


class AnalyticQContainerManager:

    _instance = None
    _lock = Lock()

    def __init__(
        self,
        runtime_config: AnalyticQContainerRuntimeConfig = AnalyticQContainerRuntimeConfig()
    ):
        self.docker = None
        self.runtime_config = runtime_config
        self.initialized = False

    async def initialize(self):
        """
        Initialize the Docker client asynchronously.
        This method should be called explicitly to initialize the class.
        """
        if not self.initialized:
            if self.docker is None:
                self.docker = aiodocker.Docker()
                self.initialized = True

    async def cleanup(self):
        """
        Cleanup the Docker client connection and reset initialization state.

        Returns:
            None
        """
        if self.docker is not None:
            await self.docker.close()
            self.docker = None
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

    async def _collect_container_logs(self, container, container_id: str):
        """Collect container logs using the correct stream handling."""
        try:
            # Get container logs
            logs = await container.log(stdout=True, stderr=True, follow=True)
            async for log_line in logs:
                # Log line is already a string in the new version
                log_line = log_line.strip()
                if log_line:
                    logger.info(f"Container {container_id} output: {log_line}")
        except Exception as e:
            logger.error(f"Error collecting logs from container {container_id}: {str(e)}")

    async def _image_exists(self, image_name: str, image_tag: str = "latest") -> bool:
        """
        Check if a Docker image exists locally.

        Args:
            image_name (str): Name of the Docker image to check.
            image_tag (str, optional): Tag of the Docker image. Defaults to "latest".

        Returns:
            bool: True if the image exists locally, False otherwise.
        """
        try:
            await self.docker.images.get(f"{image_name}:{image_tag}")
            return True
        except aiodocker.exceptions.DockerError:
            return False

    async def pull_image(self, image_name: str, image_tag: str) -> None:
        """
        Pull a Docker image from a registry.

        Args:
            image_name (str): The name of the Docker image to pull
            image_tag (str): The tag of the Docker image version to pull

        Raises:
            RuntimeError: If the image pull operation fails
        """
        try:
            await self.docker.images.pull(image_name, tag=image_tag)
            logger.info(f"Successfully pulled {image_name}:{image_tag}")
        except aiodocker.exceptions.DockerError as e:
            raise RuntimeError(f"Failed to pull image {image_name}:{image_tag}: {str(e)}")

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
        full_image = f"{image_name}:{image_tag}"
        container_id = os.urandom(8).hex()
        command_args = command_args or []
        volumes = volumes or {}

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

        try:
            container = await self.docker.containers.create(config=config)

            await container.start()
            logger.info(f"Container {container_id} started")

            logs = container.log(stdout=True, stderr=True, follow=True)

            # Wait for container completion
            # Process logs while waiting for container
            while True:
                try:
                    log_line = await anext(logs)
                    if log_line:
                        logger.info(f"Container {container_id} output: {log_line.strip()}")
                except StopAsyncIteration:
                    break
                except Exception as e:
                    logger.error(f"Error reading log line: {str(e)}")
                    break

            result = await container.wait()
            if result["StatusCode"] != 0:
                raise RuntimeError(f"Container exited with code {result['StatusCode']}")

            if file_path != "":
                output_path = list(volumes.keys())[-1]
                file_content = (output_path / file_path).read_text()
                return file_content

            return None
        except aiodocker.exceptions.DockerError as e:
            raise ScanConfigurationException(f"Docker API error: {str(e)}") from e
        finally:
            if container:
                try:
                    await container.delete(force=True)
                except Exception:
                    logger.warning(f"Failed to delete container {container_id}", exc_info=True)
