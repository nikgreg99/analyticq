import tempfile
from abc import abstractmethod
from pathlib import Path
from typing import Optional

from .container_runner import AnalyticQContainerRunner


class AnalyticQAnalyzer(AnalyticQContainerRunner):
    """A base class for running analysis in containers.

    This class extends AnalyticQContainerRunner to provide functionality for running
    analysis tasks in Docker containers. It defines the interface and basic implementation
    for analyzing codebases with configurable parameters.

    Methods:
        get_output_filename(): Abstract method that should return the output filename for analysis results.
        run_analysis(codebase_path, config_path, timeout): Runs the analysis in a container and returns results.

    Args:
        codebase_path (str): Path to the codebase to be analyzed.
        config_path (Optional[str]): Path to configuration file, if needed.
        timeout (Optional[int]): Maximum time in seconds for the analysis to complete.

    Returns:
        str: The analysis results from the container execution.

    Raises:
        ContainerError: If there's an error during container execution.
        TimeoutError: If the analysis exceeds the specified timeout.
    """

    @abstractmethod
    def get_output_filename(self) -> str:
        pass

    async def run_analysis(
        self,
        codebase_path: str,
        config_path: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> str:

        """Run the analysis in a container."""
        with tempfile.TemporaryDirectory() as tmp_dir:

            volumes = self.get_base_volumes(str(codebase_path), tmp_dir)

            # If a config path is provided, add it to the volumes
            if config_path:
                config_path = Path(config_path)
                if not config_path.exists():
                    raise FileNotFoundError(f"Config file not found: {config_path}")

                config_filename = config_path.name
                volumes.update(self.get_config_volume(str(config_path)), config_filename)

            return await self.container_manager.run_container_command(
                image_name=self.image_name,
                image_tag=self.image_tag,
                command_args=[],
                volumes=volumes,
                env_vars=None,
                timeout=timeout,
                file_path=self.get_output_filename()
            )
