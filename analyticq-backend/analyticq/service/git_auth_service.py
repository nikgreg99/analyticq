import asyncio
import logging
import os
import platform
import re
import subprocess
from pathlib import Path
from threading import Lock

import aiofiles
from analyticq.util import PathUtil

logger = logging.getLogger(__name__)


class GitAuthService:
    """ A service class for managing SSH key authentication for Git operations.

    This class implements the Singleton pattern and provides methods to manage SSH keys,
    including loading them into the SSH agent, configuring Git to use specific SSH keys,
    and extracting key properties. It handles both Windows and Unix-like operating systems.

    Attributes:
        _instance (GitAuthService): The singleton instance of the class.
        _lock (Lock): A threading lock to ensure thread-safe singleton instantiation.

    Methods:
        _is_windows_os(): Checks if the current OS is Windows.
        _start_ssh_agent(): Starts the SSH agent service.
        _is_key_loaded(ssh_key_path): Checks if an SSH key is loaded in the agent.
        load_ssh_key(ssh_key_path): Loads an SSH key into the SSH agent.
        configure_git_ssh(ssh_key_path): Configures Git to use a specific SSH key.
        get_ssh_key_properties(ssh_key_path): Retrieves properties of an SSH key.
        extract_ssh_auth_token(ssh_key_path): Extracts authentication token from SSH key.
        remove_ssh_key(ssh_key_path): Removes an SSH key from the SSH agent.

    Example:
        git_auth = GitAuthService()
        await git_auth.configure_git_ssh(Path('/path/to/ssh/key'))

    Note:
        This service requires the SSH agent to be available on the system.
        On Windows, it attempts to start the SSH agent service if not running.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def _is_windows_os(self) -> bool:
        """
        Check if the current operating system is Windows.

        Returns:
            bool: True if the operating system is Windows, False otherwise.
        """
        return platform.system().lower() == "windows"

    async def check_ssh_availability(self) -> bool:
        """
        Check if SSH is available on the system by attempting to run the SSH version command.

        Returns:
            bool: True if SSH is available and working, False otherwise.
                - Returns True if 'ssh -V' command executes successfully
                - Returns False if command fails or SSH is not found on system
        """
        try:
            await asyncio.to_thread(
                subprocess.run,
                ["ssh", "-V"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("SSH is not available ont the system")
            return False

    async def _start_ssh_agent(self) -> None:
        """
        Starts the SSH agent.

        On Windows, it attempts to start the SSH agent service using the `sc` command.
        On other operating systems, it checks if the `SSH_AUTH_SOCK` environment variable is set.
        If not, it runs the `ssh-agent` command to start the SSH agent and sets the `SSH_AUTH_SOCK`
        environment variable accordingly.

        Raises:
            subprocess.CalledProcessError: If starting the SSH agent on Windows fails.
        """
        if self._is_windows_os():
            try:
                await asyncio.to_thread(subprocess.run, ["sc", "start", "ssh-agent"], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                logger.warning("Failed to start SSH agent on Windows")
        else:
            if "SSH_AUTH_SOCK" not in os.environ:
                result = subprocess.run(["ssh-agent", "-s"],
                                        shell=True,
                                        capture_output=True,
                                        text=True)
                for line in result.stdout.split('\n'):
                    if line.startswith('SSH_AUTH_SOCK='):
                        sock_path = line.split('=')[1].strip().split(';')[0]
                        os.environ['SSH_AUTH_SOCK'] = sock_path
                        break
                    os.environ["SSH_AUTH_SOCK"] = sock_path

    async def _is_key_loaded(self, ssh_key_path: Path) -> bool:
        """
        Check if the SSH key at the given path is loaded into the SSH agent.

        Args:
            ssh_key_path (Path): The path to the SSH key file.

        Returns:
            bool: True if the SSH key is loaded, False otherwise.
        """
        try:
            result = await asyncio.to_thread(subprocess.run, ["ssh-add", "-l"], capture_output=True, text=True, check=True)
            return any(PathUtil.path_to_str(ssh_key_path) in line for line in result.stdout.splitlines())
        except subprocess.CalledProcessError:
            return False

    async def load_ssh_key(self, ssh_key_path: Path) -> None:
        if not ssh_key_path.exists():
            raise FileNotFoundError(f"SSH key not found at {ssh_key_path}")

        if not await self.check_ssh_availability():
            raise RuntimeError("SSH is not available on the system")

        await self._start_ssh_agent()

        if await self._is_key_loaded(ssh_key_path):
            logger.info("SSH key is already loaded.")

        try:
            await asyncio.to_thread(subprocess.run, ["ssh-add", PathUtil.path_to_str(ssh_key_path)], check=True)
            logger.info("SSH key loaded successfully.")
            return ssh_key_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to load SSH key: {e}")
            raise

    async def configure_git_ssh(self, ssh_key_path: Path):
        """
        Configures Git to use a specific SSH key for authentication.

        This method sets the `GIT_SSH_COMMAND` environment variable to use the provided SSH key
        for Git operations. If the SSH key is not already loaded, it will load the key first.

        Args:
            ssh_key_path (Path): The file path to the SSH key to be used for Git authentication.

        Raises:
            Exception: If there is an error loading the SSH key.
        """
        if not await self.check_ssh_availability():
            raise RuntimeError("SSH is not available on the system")

        if not await self._is_key_loaded(ssh_key_path):
            await self.load_ssh_key(ssh_key_path)

        os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o IdentitiesOnly=yes"
        logger.info("Git SSH authentication configured successfully.")

    async def get_ssh_key_properties(self, ssh_key_path: Path) -> dict:
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["ssh-keygen", "-l", "-f", PathUtil.path_to_str(ssh_key_path)],
                capture_output=True,
                text=True,
                check=True
            )

            parts = result.stdout.strip().split()
            key_details = {
                "bits": parts[0],
                "fingerprint": parts[1],
                "type": parts[3] if len(parts) > 3 else "Unknown",
                "comment": parts[4] if len(parts) > 4 else ""
            }

            return {
                "ssh_key_path": PathUtil.path_to_str(ssh_key_path),
                "key_details": key_details,
                "key_type": key_details.get("type", "Unknown"),
                "key_fingerprint": key_details.get("fingerprint", ""),
                "git_ssh_command": f"ssh -i {ssh_key_path} -o IdentitiesOnly=yes"
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract SSH key details: {e}")
            return {}

    async def extract_ssh_auth_token(self, ssh_key_path: Path) -> str:
        try:
            # Read SSH key content
            with aiofiles.open(ssh_key_path, 'r') as key_file:
                key_content = await key_file.read()

        # Extract token-like patterns
            token_patterns = [
                r'(?:token|auth_token)\s*[:=]\s*["\'](.*?)["\']',
                r'[A-Za-z0-9+/]{40,}'  # Base64-like tokens
            ]

            for pattern in token_patterns:
                match = re.search(pattern, key_content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            # Fallback: use key filename or fingerprint
            return await self.get_ssh_key_properties(ssh_key_path).get('fingerprint', '')

        except Exception as e:
            logger.error(f"Failed to extract auth token: {e}")
            return ''

    async def remove_ssh_key(self, ssh_key_path: Path) -> None:
        """
        Removes an SSH key from the SSH agent.

        Args:
            ssh_key_path (Path): The path to the SSH key to be removed.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If the SSH key removal process fails.

        Logs:
            An error message if the SSH key removal process fails.
        """
        if not await self._is_key_loaded(ssh_key_path):
            return None

        try:
            await asyncio.to_thread(subprocess.run, ["ssh-add", "-d"], PathUtil.path_to_str(ssh_key_path), check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove SSH key: {e}")
