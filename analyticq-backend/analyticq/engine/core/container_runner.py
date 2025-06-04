import logging
import os
import shutil
from abc import ABC
from pathlib import Path
from typing import Dict, Optional

from analyticq.manager import AnalyticQContainerManager

logger = logging.getLogger(__name__)


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

    def get_base_volumes(self, code_path: str, tmp_dir: str) -> Dict[Path, Dict[str, str]]:
        """
        The function creates a dictionary mapping local paths to their container mount points,
        setting up the basic volume structure needed for code execution.

        Args:
            code_path (str): Local path containing the code to be executed
            tmp_dir (str): Local temporary directory path for output storage

        Returns:
            Dict[Path, Dict[str, str]]: Dictionary containing volume mappings with:
                - Key: Path object of local directory
                - Value: Dictionary with:
                    - 'bind': Container mount point
                    - 'mode': Access mode ('ro' for read-only, 'rw' for read-write)

        Example:
            {
                Path('/local/code'): {'bind': '/code', 'mode': 'ro'},
                Path('/local/tmp'): {'bind': '/output', 'mode': 'rw'}
            }
        """
        return {
            Path(code_path): {"bind": "/code", "mode": "rw"},
            Path(tmp_dir): {"bind": "/output", "mode": "rw"}
        }

    def get_config_volume(self, config_path: str, config_filename: str) -> Dict[Path, Dict[str, str]]:
        """
        This method generates a dictionary configuration for Docker volume mounting,
        specifically for configuration files.

        Args:
            config_path (str): The path to the configuration file on the host system
            config_filename (str): The name of the configuration file

        Returns:
            Dict[Path, Dict[str, str]]: A dictionary containing volume binding configuration
                where the key is Path object and value is a dictionary with:
                - 'bind': The mount path inside container (/config/<filename>)
                - 'mode': The mount mode ('ro' for read-only)

        Example:
            >>> get_config_volume('/path/to/config', 'settings.yaml')
            {Path('/path/to/config'): {'bind': '/config/settings.yaml', 'mode': 'ro'}}
        """
        return {Path(config_path): {"bind": f"/config/{config_filename}", "mode": "ro"}}

    async def run_analysis(
        self,
        codebase_path: str,
        config_path: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> str:
        """Run the analysis in a container."""

        # Use the prepare_working_directories method to create persistent temp dirs
        working_dirs = self.prepare_working_directories()

        try:
            work_code_dir = Path(working_dirs["code_dir"])
            work_output_dir = Path(working_dirs["output_dir"])

            # Copy codebase to working directory
            codebase_source = Path(codebase_path)
            if codebase_source.exists():
                logger.info(f"Copying codebase from {codebase_source} to {work_code_dir}")
                if codebase_source.is_file():
                    shutil.copy2(codebase_source, work_code_dir)
                else:
                    # Copy entire directory contents
                    for item in codebase_source.iterdir():
                        if item.is_file():
                            shutil.copy2(item, work_code_dir)
                        else:
                            shutil.copytree(item, work_code_dir / item.name, dirs_exist_ok=True)

                # Verify files were copied
                copied_files = list(work_code_dir.rglob("*"))
                logger.info(f"Copied {len(copied_files)} items to working directory")

            else:
                raise FileNotFoundError(f"Codebase path does not exist: {codebase_path}")

            # Prepare volumes with working directories
            volumes = self.get_base_volumes(str(work_code_dir), str(work_output_dir))

            if config_path:
                # Copy config file to working directory
                config_source = Path(config_path)
                if config_source.exists():
                    work_config_dir = Path(working_dirs["work_dir"]) / "config"
                    work_config_dir.mkdir(exist_ok=True)
                    work_config_file = work_config_dir / config_source.name
                    shutil.copy2(config_source, work_config_file)

                    config_volumes = self.get_config_volume(str(work_config_file), config_source.name)
                    volumes.update(config_volumes)

            # Log volume mappings for debugging
            logger.info("Volume mappings:")
            for local_path, mount_info in volumes.items():
                logger.info(f"  {local_path} -> {mount_info['bind']} ({mount_info['mode']})")
                # Verify local path exists and has content
                if local_path.exists():
                    if local_path.is_dir():
                        file_count = len(list(local_path.rglob("*")))
                        logger.info(f"    Directory contains {file_count} items")
                    else:
                        logger.info(f"    File size: {local_path.stat().st_size} bytes")
                else:
                    logger.error(f"    Path does not exist: {local_path}")

            return await self.container_manager.run_container_command(
                image_name=self.image_name,
                image_tag=self.image_tag,
                command_args=[],
                volumes=volumes,
                env_vars=None,
                timeout=timeout,
                file_path=self.get_output_filename()
            )

        finally:
            # Clean up working directories
            try:
                work_dir = Path(working_dirs["work_dir"])
                if work_dir.exists():
                    shutil.rmtree(work_dir)
                    logger.info(f"Cleaned up working directory: {work_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up working directory: {e}")

    def get_output_filename(self) -> str:
        """
        Return the expected output filename for the analysis.
        This should be overridden by concrete implementations.
        """
        raise NotImplementedError("Subclasses must implement get_output_filename()")

    def prepare_working_directories(self, base_tmp_dir: str = "/tmp") -> Dict[str, str]:
        """
        Prepare working directories for container execution.

        Note: This creates directories in /tmp but does NOT use tempfile.TemporaryDirectory()
        to avoid automatic cleanup before container execution.

        Args:
            base_tmp_dir (str): Base temporary directory path

        Returns:
            Dict[str, str]: Dictionary with prepared paths
        """
        import uuid

        # Generate unique identifier for this run
        run_id = uuid.uuid4().hex[:8]
        base_tmp_dir = os.getenv("ANALYTICQ_TMP_BASE", "/tmp")

        # Create working directories in /tmp (persistent until manual cleanup)
        work_dir = Path(base_tmp_dir) / f"analyticq-{run_id}"
        code_dir = work_dir / "code"
        output_dir = work_dir / "output"

        # Ensure directories exist
        code_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Prepared working directories: code={code_dir}, output={output_dir}")

        return {
            "work_dir": str(work_dir),
            "code_dir": str(code_dir),
            "output_dir": str(output_dir),
            "run_id": run_id
        }

    def merge_volumes(self, *volume_dicts: Dict[Path, Dict[str, str]]) -> Dict[Path, Dict[str, str]]:
        """
        Merge multiple volume dictionaries into one.

        Args:
            *volume_dicts: Variable number of volume dictionaries to merge

        Returns:
            Dict[Path, Dict[str, str]]: Merged volume dictionary
        """
        merged = {}
        for vol_dict in volume_dicts:
            merged.update(vol_dict)
        return merged
