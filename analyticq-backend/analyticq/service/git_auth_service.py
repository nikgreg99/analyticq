import logging
import os
import platform
import subprocess
from pathlib import Path

from analyticq.util import PathUtil

logger = logging.getLogger(__name__)


class GitAuthService:

    def _is_windows(self) -> bool:
        return platform.system().lower() == "windows"

    def _start_ssh_agent(self) -> None:
        if self._is_windows():
            try:
                subprocess.run(["sc", "start", "ssh-agent"], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                logger.warning("Failed to start SSH agent on Windows")
        else:
            if "SSH_AUTH_SOCK" not in os.environ:
                result = subprocess.run(["eval", "$(ssh-agent -s)"], shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    os.environ["SSH_AUTH_SOCK"] = result.stdout.split("=")[1].strip().split(";")[0]

    def _is_key_loaded(self, ssh_key_path: Path) -> bool:
        try:
            result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True, check=True)
            return PathUtil.path_to_str(ssh_key_path) in result.stdout
        except subprocess.CalledProcessError:
            return False

    def load_ssh_key(self, ssh_key_path: Path) -> None:
        if not ssh_key_path.exists():
            logger.error(f"SSH key not found at {ssh_key_path}")
            raise FileNotFoundError(f"SSH key not found at {ssh_key_path}")

        self._start_ssh_agent()

        if self._is_key_loaded(ssh_key_path):
            logger.info("SSH key is already loaded.")

        try:
            subprocess.run(["ssh-add", PathUtil.path_to_str(ssh_key_path)], check=True)
            logger.info("SSH key loaded successfully.")
            return ssh_key_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to load SSH key: {e}")
            raise

    def configure_git_ssh(self, ssh_key_path: Path):
        if not self._is_key_loaded(ssh_key_path):
            self.load_ssh_key(ssh_key_path)
        os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o IdentitiesOnly=yes"
        logger.info("Git SSH authentication configured successfully.")

    def remove_ssk_key(self, ssh_key_path: Path) -> None:
        if not self._is_key_loaded(ssh_key_path):
            return None

        try:
            subprocess.run(["ssh-add", "d"], PathUtil.path_to_str(ssh_key_path), check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove SSH key: {e}")
