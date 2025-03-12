import asyncio
import logging
import os
import re
import shutil
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Callable, Optional, Type
from urllib.parse import urlparse

from analyticq.config import AnalyticQBaseConfig
from analyticq.exception import (CloneLocalRepositoryException,
                                 CloneLocalScriptException,
                                 CloneRemoteRepositoryException,
                                 CodebaseNotFoundException,
                                 CodebaseUnknownTypeException)
from analyticq.service import GitAuthService
from analyticq.util import PathUtil
from dependency_injector.wiring import Provide, inject
from git import Repo
from git.exc import GitCommandError

logger = logging.getLogger(__name__)


class CodebaseClonerPathType(Enum):
    """Enumeration for codebase URL TYPE"""
    LOCAL_REPO = "local"
    REMOTE_REPO = "remote"
    GIT_REPO = "repo"
    SCRIPT = "script"
    UNKNOWN = "unknown"


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

    @inject
    def __init__(self,
                 git_auth_service: GitAuthService = Provide[GitAuthService]):
        if not hasattr(self, "_initialized"):
            codebase_config = AnalyticQBaseConfig.get("codebase")
            self.default_branch = codebase_config["default_branch"]
            self._initialized = True
            self.git_auth_service = git_auth_service

    def _get_codebase_type(self, path: str) -> CodebaseClonerPathType:
        """
        Determine the type of codebase path.

        Args:
            path (str): The given path of the codebase.

        Returns:
            CodebaseClonerPathType: Deteced path type
        """
        parsed = urlparse(path)
        # Check if it's a remote repository
        if parsed.scheme in {"http", "https", "git"} or re.match(r"^(git@|https?://).+\.git$", path):
            return CodebaseClonerPathType.REMOTE_REPO

        if not os.path.exists(path):
            return CodebaseClonerPathType.UNKNOWN

        if os.path.isfile(path):
            return CodebaseClonerPathType.SCRIPT  # Prioritize script detection

        if os.path.isdir(path):
            return (
                CodebaseClonerPathType.GIT_REPO
                if os.path.exists(os.path.join(path, ".git"))
                else CodebaseClonerPathType.LOCAL_REPO
            )

        return CodebaseClonerPathType.UNKNOWN  # Fallback case, but should rarely be hit

    def _get_protocol(self, codebase_url: str) -> CodebaseClonerProtocolType:
        """
        Determine the protocol type from the codebase URL.

        Args:
            codebase_url: (str) The URL of where the remote codebase is located.

        Returns:
            CodebaseClonerProtocolType: Detected URL protocol
        """
        parsed_url = urlparse(codebase_url)
        scheme = parsed_url.scheme
        if not scheme or scheme == "ssh":
            return CodebaseClonerProtocolType.SSH
        if scheme in ["http", "https"]:
            return CodebaseClonerProtocolType(scheme)
        return CodebaseClonerProtocolType.HTTPS

    def _check_existing_path(self, path: Path) -> bool:
        """
        Check if a path already exists.

        Args:
            path (Path): Path to check for existence.

        Returns:
            bool: True if path exists, False otherwise.

        Notes:
            If path exists, logs an info message indicating the codebase already exists.
        """
        outcome = path.exists()
        if outcome:
            logger.info(f"Codebase already exists at {path}. Skipping cloning...")
        return outcome

    async def _clone_with_path_check(
            self,
            source_path: Path,
            dest_path: Path,
            operation: Callable,
            success_message: str,
            exception_class: Type[Exception],
    ):
        if self._check_existing_path(dest_path):
            return dest_path

        try:
            await asyncio.to_thread(operation, source_path, dest_path)
            logger.info(success_message)
            return dest_path
        except Exception as e:
            raise exception_class(f"Failed to perform operation from {source_path} to {dest_path}: {e}")

    async def clone_remote_codebase(
        self,
        codebase_url: str,
        branch: str = None,
        tag: Optional[str] = None,
        ssh_auth_token: Optional[str] = None,
        protocol: CodebaseClonerProtocolType = CodebaseClonerProtocolType.HTTPS
    ) -> Path:
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
        repo_name = codebase_url.split("/")[-1].replace(".git", "")
        repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

        if self._check_existing_path(repo_path):
            return repo_path

        ref = tag if tag else branch or self.default_branch
        logger.info(f"Cloning codebase from {codebase_url} at {('tag ' + tag) if tag else ('branch ' + ref)} using {protocol.value}...")

        auth_url = codebase_url

        if protocol == CodebaseClonerProtocolType.SSH:
            auth_url = auth_url.replace("https://", f"https://{ssh_auth_token}@")

        try:
            await asyncio.to_thread(Repo.clone_from, auth_url, repo_path, branch=ref)
            logger.info(f"Repository cloned succesfully at {repo_path}")
        except GitCommandError as e:
            raise CloneRemoteRepositoryException(f"Failed to clone repository from {codebase_url}: {e}")
        return repo_path

    async def clone_local_codebase(self, source_path: str) -> Path:
        """
        Clone a local codebase repository.

        Args:
            source_codebase_path (str): Path to the source codebase directory.

        Returns:
            Path: Path to the copied repository.
        Raises:

            CodebaseNotFoundException: If the source path does not exist.
            CloneLocalRepositoryException: If copying fails.
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise CodebaseNotFoundException(f"Source codebase directory does not exists at: {source_path}")

        dest_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / source_path.name

        if self._check_existing_path(dest_path):
            return dest_path

        logger.info(f"Copying local codebase from {source_path} to {dest_path}")
        path = await self._clone_with_path_check(
            source_path,
            dest_path,
            shutil.copytree,
            f"Codebase copied successfully to {dest_path}",
            CloneLocalRepositoryException,
        )
        return path

    async def clone_local_script(self, script_path: str) -> Path:
        """
        Clone a local script.

        Args:
            script_path (str): Path to the source script file.

        Returns:
            Path: Path to the copied script.

        Raises:
            CodebaseNotFoundException: If the codebase doensn't exist
            CloneLocalScriptException If the cloning script operation failed
        """
        script_path = Path(script_path)
        script_dest_path = PathUtil.get_codebase_scripts_AnalyticQ_path() / script_path.name

        if not script_path.exists():
            raise CodebaseNotFoundException(f"Script source path does not exists at: {script_path}")

        if self._check_existing_path(script_dest_path):
            return script_dest_path

        return await self._clone_with_path_check(
            script_path,
            script_dest_path,
            shutil.copy,
            f"Script copied successfully to {script_dest_path}",
            CloneLocalScriptException,
        )

    async def clone(self, codebase_url: str, **kwargs) -> Path:
        """
        Clone a codebase from a given URL.

        This method determines the type of the codebase URL and performs the appropriate
        cloning operation based on the type. It supports cloning from remote repositories,
        local repositories, and local scripts.

        Args:
            codebase_url (str): The URL of the codebase to clone.
            **kwargs: Additional keyword arguments that may include:
                - branch (str): The branch to clone from the remote repository. Defaults to the default branch.
                - tag (str): The tag to clone from the remote repository. Defaults to None.
                - ssh_key_path (str): The path to the SSH key for authentication. Defaults to None.

        Returns:
            Path: The path to the cloned codebase.

        Raises:
            CodebaseUnknownTypeException: If the codebase type is unknown.
        """
        codebase_url_type = self._get_codebase_type(codebase_url)
        path = None
        match codebase_url_type:
            case CodebaseClonerPathType.REMOTE_REPO:
                credentials = None
                if kwargs is not None:
                    branch = kwargs.get("branch", self.default_branch)
                    tag = kwargs.get("tag", None)
                    ssk_key_path = kwargs.get("ssh_key_path", None)
                    protocol = self._get_protocol(codebase_url)
                    if ssk_key_path:
                        await self.git_auth_service.configure_git_ssh(ssk_key_path)
                        credentials = await self.git_auth_service.extract_ssh_auth_token(ssk_key_path)
                    path = await self.clone_remote_codebase(codebase_url, branch, tag, credentials, protocol)
            case CodebaseClonerPathType.GIT_REPO | CodebaseClonerPathType.LOCAL_REPO:
                path = await self.clone_local_codebase(codebase_url)
            case CodebaseClonerPathType.SCRIPT:
                path = await self.clone_local_script(codebase_url)
            case _:
                raise CodebaseUnknownTypeException(f"Unknown codebase type: {codebase_url_type}")
        return path
