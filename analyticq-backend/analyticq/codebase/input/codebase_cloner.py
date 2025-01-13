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
from analyticq.utils import (create_folder_if_not_exists,
                             get_codebase_repositories_folder_path,
                             get_codebase_scripts_folder_path)
from git import GitCommandError, Repo

logger = logging.getLogger(__name__)


class CodebaseProtocolType(Enum):
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
        codebase_config = AnalyticQBaseConfig.get("codebase")
        self.default_branch = codebase_config["default_branch"]

    def _get_protocol(self, codebase_url: str):
        parsed_codebase_url = urlparse(codebase_url)
        if parsed_codebase_url.scheme == "":
            return CodebaseProtocolType.SSH
        elif parsed_codebase_url.scheme in ["http", "https"]:
            return CodebaseProtocolType(parsed_codebase_url.scheme)
        return CodebaseProtocolType.HTTPS

    async def clone_remote_codebase(self, codebase_url: str, branch: str = None, credentials: str = None):
        protocol = self._get_protocol(codebase_url)
        repo_name = codebase_url.split("/")[-1].replace(".git", "")
        repo_path = get_codebase_repositories_folder_path() / repo_name

        if not create_folder_if_not_exists(repo_path.parent):
            logger.info(f"{repo_path.parent} creation already exists")

        if repo_path.exists():
            logger.info(f"Codebase already exists locally at {repo_path}. Skipping cloning...")
            return None

        if branch is None:
            branch = self.default_branch

        logger.info(f"Cloning codebase from {codebase_url} at branch {branch} using protocol {protocol}...")

        if credentials and credentials.auth_token:
            codebase_url = codebase_url.replace("https://", f"https://{credentials.auth_token}@")
        try:
            await asyncio.to_thread(Repo.clone, codebase_url, repo_path, branch=branch)
            logger.info(f"Repository cloned succesfully at {repo_path}")
        except GitCommandError:
            raise CloneRemoteRepositoryException(f"Failed to clone repository from {codebase_url}")
        return repo_path

    async def clone_local_codebase(self, source_codebase_path):
        source_codebase_path = Path(source_codebase_path)
        if not source_codebase_path.exists():
            raise CodebaseNotFoundException(f"Source codebase directory does not exist at: {source_codebase_path}")

        repo_name = source_codebase_path.name
        dest_codebase_path = get_codebase_repositories_folder_path() / repo_name

        if not create_folder_if_not_exists(dest_codebase_path.parent):
            logger.warning(f"{dest_codebase_path.parent} creation already exists")

        if dest_codebase_path.exists():
            logger.info(f"Codebase already exists locally at {dest_codebase_path}. Skipping copying...")
            return None

        logger.info(f"Copying local codebase from {source_codebase_path} to {dest_codebase_path}")

        try:
            await asyncio.to_thread(shutil.copytree, source_codebase_path, dest_codebase_path)
        except Exception as e:
            raise CloneLocalRepositoryException(f"Failed to copy codebase from {source_codebase_path} to {dest_codebase_path}: {str(e)}")
        logger.info(f"Codebase copied succesfully at {dest_codebase_path}")

    async def clone_local_script(self, script_path):
        script_path = Path(script_path)
        script_codebase_path = get_codebase_scripts_folder_path()

        if not script_path.exists():
            raise CodebaseNotFoundException.error(f"Script source path does not exist at: {script_codebase_path}")

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
