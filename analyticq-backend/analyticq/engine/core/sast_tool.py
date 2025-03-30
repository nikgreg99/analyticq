from abc import ABC
from pathlib import Path
from typing import Optional, Set

import aiodocker.exceptions
from analyticq.exception import ScanConfigurationException
from analyticq.manager import AnalyticQContainerManager

from .analyzer import AnalyticQAnalyzer
from .models import AnalyticQSASTScanResultModel
from .result_parser import AnalyticQResultParser
from .tool_strategy_output import StringToolFormatter


class AnalyticQSASTTool(ABC):
    """Abstract base class representing a Static Application Security Testing (SAST) tool.

    This class provides a common interface for different SAST tools to be integrated into
    the AnalyticQ system. It handles container-based tool execution and result parsing.

    Attributes:
        supported_languages (Set[str]): Set of programming languages supported by the SAST tool.
        analyzer (AnalyticQAnalyzer): Component responsible for running the analysis.
        parser (AnalyticQResultParser): Component responsible for parsing scan results.
        container_manager (AnalyticQContainerManager): Manager for container operations.
        image_name (str): Name of the Docker image for the SAST tool.
        image_tag (str): Tag of the Docker image for the SAST tool.

    Example:
        ```python
        class MySASTTool(AnalyticQSASTTool):
            supported_languages = {'python', 'javascript'}

            def __init__(self):
                super().__init__(
                    analyzer=MyAnalyzer(),
                    parser=MyParser(),
                    container_manager=MyContainerManager(),
                    image_name="my-sast-tool",
                    image_tag="latest"
        ```
    """
    supported_languages: Set[str] = set()

    def __init__(self,
                 analyzer: AnalyticQAnalyzer,
                 parser: AnalyticQResultParser,
                 container_manager: AnalyticQContainerManager,
                 image_name: str,
                 image_tag: str):
        self.analyzer = analyzer
        self.parser = parser
        self.container_manager = container_manager
        self.image_name = image_name
        self.image_tag = image_tag

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

    async def run_scan(
        self,
        codebase_path: str,
        config_path: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> AnalyticQSASTScanResultModel:
        try:
            code_path = Path(codebase_path)
            if not code_path.exists():
                raise ScanConfigurationException(
                    f"Code path does not exist for {self.image_name}: {code_path}"
                )

            if config_path:
                config_file_path = Path(config_path)
                if not config_file_path.exists():
                    raise ScanConfigurationException(
                        f"Config file not found for {self.image_name}:  {config_file_path}"
                    )

            raw_result = await self.analyzer.run_analysis(
                codebase_path=code_path,
                config_path=config_path,
                timeout=timeout
            )
            dict_output = StringToolFormatter.from_str_to_dict(raw_result)
            print(dict_output)
            return self.parser.parse_scan_result(dict_output)

        except ValueError as e:
            raise ScanConfigurationException(
                f"Invalid configuration: {str(e)}"
            ) from e

    @classmethod
    def get_supported_languages(cls) -> Set[str]:
        """Return the set of languages supported by this tool"""
        return cls.supported_languages
