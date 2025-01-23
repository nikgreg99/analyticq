import logging
import os
import platform
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class GitAuthService:

    def __init__(self, ssh_key_path: str = "~/.ssh/id_rsa"):
        self.ssh_key_path = Path(os.path.expanduser(ssh_key_path))

    def _is_windows(self) -> bool:
        return platform.system().lower() == "windows"

    def _is_key_loaded(self) -> bool:
        try:
            result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True, check=True)
            return str(self.ssh_key_path) in result.stdout
        except subprocess.CalledProcessError:
            return False

    def load_ssh_key(self):
        if not self.ssh_key_path.exists():
            logger.error(f"SSH key not found at {self.ssh_key_path}")
            raise FileNotFoundError(f"SSH key not found at {self.ssh_key_path}")

        # self._start_ssh_agent()

        if self._is_key_loaded():
            logger.info("SSH key is already loaded.")

        try:
            subprocess.run(["ssh-add", str(self.ssh_key_path)], check=True)
            logger.info("SSH key loaded successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to load SSH key: {e}")
            raise

    def configure_git_ssh(self):
        os.environ["GIT_SSH_COMMAND"] = f"ssh -i {self.ssh_key_path} -o IdentitiesOnly=yes"
        logger.info("Git SSH authentication configured successfully.")
