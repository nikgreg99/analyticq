import tempfile
from abc import abstractmethod
from typing import Optional

from .container_runner import AnalyticQContainerRunner


class AnalyticQAnalyzer(AnalyticQContainerRunner):

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

            if config_path:
                volumes.update(self.get_config_volume(str(config_path)))

            return await self.container_manager.run_container_command(
                image_name=self.image_name,
                image_tag=self.image_tag,
                command_args=[],
                volumes=volumes,
                env_vars=[],
                timeout=timeout,
                file_path=self.get_output_filename()
            )
