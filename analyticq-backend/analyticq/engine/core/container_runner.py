from abc import ABC
from pathlib import Path
from typing import Dict

from analyticq.manager import AnalyticQContainerManager


class AnalyticQContainerRunner(ABC):
    """Base class for container-based operations."""

    def __init__(
        self,
        container_manager: AnalyticQContainerManager,
        image_name: str,
        image_tag: str
    ):
        self.container_manager = container_manager
        self.image_name = image_name
        self.image_tag = image_tag

    def get_base_volumes(self, code_path: str, tmp_dir: str) -> Dict[str, Dict[str, str]]:
        """Get base volume configuration."""
        return {
            Path(code_path): {"bind": "/code", "mode": "ro"},
            Path(tmp_dir): {"bind": "/output", "mode": "rw"}
        }

    def get_config_volume(self, config_path: str, config_filename: str) -> Dict[str, Dict[str, str]]:
        """Get config file volume configuration."""
        return {config_path: {"bind": f"/config/{config_filename}", "mode": "ro"}}
