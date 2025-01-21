import asyncio
import logging
import shutil
from enum import Enum
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

from analyticq.config import AnalyticQBaseConfig
from analyticq.exception import (CloneLocalRepositoryException,
                                 CloneLocalScriptException,
                                 CloneRemoteRepositoryException,
                                 CodebaseNotFoundException)
from analyticq.util import PathUtil
from git import Repo
from git.exc import GitCommandError

logger = logging.getLogger(__name__)


class CodebaseClonerProtocolType(Enum):
    """Enumeration for codebase protocol types."""
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"


class CodebaseCloner:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            codebase_config = AnalyticQBaseConfig.get("codebase")
            self.default_branch = codebase_config["default_branch"]
            self.initialized = True

    def _get_protocol(self, codebase_url: str):
        """Determine the protocol type from the codebase URL."""
        parsed_url = urlparse(codebase_url)
        scheme = parsed_url.scheme
        if not scheme:
            return CodebaseClonerProtocolType.SSH
        if scheme in ["http", "https"]:
            return CodebaseClonerProtocolType(scheme)
        return CodebaseClonerProtocolType.HTTPS

    async def clone_remote_codebase(self, codebase_url: str, branch: str = None, tag: str = None, credentials: str = None):
        """
        Clone a remote codebase repository.

        Args:
            codebase_url (str): URL of the remote repository.
            branch (str): Branch to clone. Defaults to default branch.
            tag (str): Tag to clone. If provided, overrides branch.
            credentials (str): Authentication token for the repository.

        Returns:
            Path: Path to the cloned repository.
        """
        protocol = self._get_protocol(codebase_url)
        repo_name = codebase_url.split("/")[-1].replace(".git", "")
        repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

        print(str(repo_path))

        if repo_path.exists():
            logger.info(f"Codebase already exists locally at {repo_path}. Skipping cloning...")
            return None

        if tag:
            ref = tag
            logger.info(f"Cloning codebase from {codebase_url} by tag {tag} using protocol {protocol}..")
        else:
            if branch is None:
                branch = self.default_branch
            ref = branch
            logger.info(f"Cloning codebase from {codebase_url} at branch {branch} using protocol {protocol}...")

        if credentials and credentials.auth_token:
            codebase_url = codebase_url.replace("https://", f"https://{credentials.auth_token}@")

        try:
            await asyncio.to_thread(Repo.clone_from, codebase_url, repo_path, branch=ref)
            logger.info(f"Repository cloned succesfully at {repo_path}")
        except GitCommandError:
            raise CloneRemoteRepositoryException(f"Failed to clone repository from {codebase_url}")
        return repo_path

    async def clone_local_codebase(self, source_codebase_path: str):
        """
        Clone a local codebase repository.

        Args:
            source_codebase_path (str): Path to the source codebase directory.

        Returns:
            Path: Path to the copied repository.
        """
        source_codebase_path = Path(source_codebase_path)
        if not source_codebase_path.exists():
            raise CodebaseNotFoundException(f"Source codebase directory does not exists at: {source_codebase_path}")

        repo_name = source_codebase_path.name
        dest_codebase_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

        if dest_codebase_path.exists():
            logger.info(f"Codebase already exists locally at {dest_codebase_path}. Skipping copying...")
            return None

        logger.info(f"Copying local codebase from {source_codebase_path} to {dest_codebase_path}")

        try:
            await asyncio.to_thread(shutil.copytree, source_codebase_path, dest_codebase_path)
        except Exception as e:
            raise CloneLocalRepositoryException(f"Failed to copy codebase from {source_codebase_path} to {dest_codebase_path}: {str(e)}")
        logger.info(f"Codebase copied succesfully at {dest_codebase_path}")
        return dest_codebase_path

    async def clone_local_script(self, script_path: str):
        """
        Clone a local script.

        Args:
            script_path (str): Path to the source script file.

        Returns:
            Path: Path to the copied script.
        """
        script_path = Path(script_path)
        script_codebase_path = PathUtil.get_codebase_scripts_AnalyticQ_path()

        if not script_path.exists():
            raise CodebaseNotFoundException(f"Script source path does not exists at: {script_codebase_path}")

        script_dest_path = script_codebase_path / script_codebase_path.name

        if script_dest_path.exists():
            logger.warning(f"Script already exists locally at {script_dest_path}. Skipping script copying...")
            return None

        logger.info(f"Copying script from {script_codebase_path} to {script_dest_path}...")
        try:
            await asyncio.to_thread(shutil.copy, script_path, script_dest_path)
        except Exception as e:
            raise CloneLocalScriptException(e)
        logger.info(f"Failed to copy local script from {script_codebase_path} to {script_dest_path}")
        return script_dest_path
