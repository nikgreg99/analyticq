import logging
from abc import ABC, abstractmethod
from typing import Optional

import aiodocker.exceptions
from analyticq.exception import ScanConfigurationException
from analyticq.manager import AnalyticQContainerManager

from .models import AnalyticQSASTScanResult


class AnalyticQSASTTool(ABC):

    def __init__(self, container_manager: AnalyticQContainerManager, image_name: str, image_tag: str):
        self.container_manager = container_manager
        self.image_name = image_name
        self.image_tag = image_tag
        self.logger = logging.getLogger(__name__)

    async def install(self) -> None:
        """Install the required container image for the corrispondent SAST tool.

        This asynchronous method checks if the required container image exists and
        pulls it if necessary.

        Raises:
            ScanConfigurationException: If there are issues pulling the container image.
        """
        await self.container_manager.initialize()
        try:
            if not await self.container_manager._image_exists(self.image_name, self.image_tag):
                await self.container_manager.pull_image(self.image_name, self.image_tag)
        except aiodocker.exceptions.DockerError as e:
            raise ScanConfigurationException(
                f"Failed to install container image: {str(e)}"
            ) from e

    @abstractmethod
    async def run_scan(
        self,
        codebase_path: str,
        config_path: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> AnalyticQSASTScanResult:
        """Run a security analysis scan on the specified codebase.

        This asynchronous method orchestrates  a Static Application Security Testing (SAST) scan
        between the Analayzer and the Parser

        Args:
            codebase_path (str): The file system path to the codebase to be analyzed.
            config_path (Optional[str], optional): Path to a custom configuration file for the scan. Defaults to None.
            timeout (Optional[int], optional): Maximum time in seconds to wait for scan completion. Defaults to None.

        Returns:
            AnalyticqSASTScanResult: The results of the security analysis scan containing found vulnerabilities
            and other relevant scan information.

        Raises:
            ScanTimeoutError: If the scan exceeds the specified timeout duration.
            ScanConfigurationError: If there are issues with the scan configuration.
            CodebaseNotFoundError: If the specified codebase path does not exist.
        """
        pass
