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
        """
        The function creates a dictionary mapping local paths to their container mount points,
        setting up the basic volume structure needed for code execution.
        Args:
            code_path (str): Local path containing the code to be executed
            tmp_dir (str): Local temporary directory path for output storage
        Returns:
            Dict[str, Dict[str, str]]: Dictionary containing volume mappings with:
                - Key: Path object of local directory
                - Value: Dictionary with:
                    - 'bind': Container mount point
                    - 'mode': Access mode ('ro' for read-only, 'rw' for read-write)
        Example:
            {
                Path('/local/code'): {'bind': '/code', 'mode': 'ro'},
                Path('/local/tmp'): {'bind': '/output', 'mode': 'rw'}
        """
        return {
            Path(code_path): {"bind": "/code", "mode": "rw"},
            Path(tmp_dir): {"bind": "/output", "mode": "rw"}
        }

    def get_config_volume(self, config_path: str, config_filename: str) -> Dict[str, Dict[str, str]]:
        """
        This method generates a dictionary configuration for Docker volume mounting,
        specifically for configuration files.

        Args:
            config_path (str): The path to the configuration file on the host system
            config_filename (str): The name of the configuration file

        Returns:
            Dict[str, Dict[str, str]]: A dictionary containing volume binding configuration
                where the key is the host path and value is a dictionary with:
                - 'bind': The mount path inside container (/config/<filename>)
                - 'mode': The mount mode ('ro' for read-only)

        Example:
            >>> get_config_volume('/path/to/config', 'settings.yaml')
            {'/path/to/config': {'bind': '/config/settings.yaml', 'mode': 'ro'}}
        """
        return {config_path: {"bind": f"/config/{config_filename}", "mode": "ro"}}
