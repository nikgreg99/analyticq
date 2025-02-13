import tempfile
from pathlib import Path
from typing import Optional

from analyticq.engine.core.analyzer import AnalyticQAnalyzer
from analyticq.manager import AnalyticQContainerManager


class PylintAnalyzer(AnalyticQAnalyzer):

    def __init__(self, container_manager: AnalyticQContainerManager, image_name: str, image_tag: str):
        self.container_manager = container_manager
        self.image_name = image_name
        self.image_tag = image_tag
        self.pylint_output_file = "pylint-report.json"

    async def run_analysis(
        self,
        codebase_path: str,
        config_path: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:

            volumes = {
                codebase_path: {"bind": "/code", "mode": "ro"},
                Path(tmp_dir): {"bind": "/output", "mode": "rw"}
            }

            if config_path:
                volumes[config_path] = {"bind": ".pylintrc", "mode": "ro"}

            results = await self.container_manager.run_container_command(
                image_name=self.image_name,
                image_tag=self.image_tag,
                command_args=[],
                volumes=volumes,
                env_vars=[],
                timeout=timeout,
                file_path=self.pylint_output_file
            )

            return results
