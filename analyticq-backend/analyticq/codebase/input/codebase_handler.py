import asyncio
import logging
import shutil
from enum import Enum
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

from analyticq.exception import CloneRepositoryError
from analyticq.utils import (create_folder_if_not_exists,
                             get_codebase_repos_path, get_codebase_script_path)
from git import GitCommandError, Repo

logger = logging.getLogger(__name__)


class CodebaseProtocolType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"


class CodebaseHadler:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, base_dir: str, config_manager):
        self.base_dir = base_dir
        self.config_manager = config_manager

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
        repo_path = get_codebase_repos_path() / repo_name

        if not create_folder_if_not_exists(repo_path.parent):
            logger.info(f"{repo_path.parent} creation already exists")

        if repo_path.exists():
            logger.info(f"Codebase already exists locally at {repo_path}. Skipping cloning...")
            return repo_path

        branch = branch or self.config_manager.get("default_branch", "main")
        logger.info(f"Cloning codebase from {codebase_url} at branch {branch} using protocol {protocol}...")

        if credentials and credentials.auth_token:
            codebase_url = codebase_url.replace("https://", f"https://{credentials.auth_token}@")
        try:
            await asyncio.to_thread(Repo.clone, codebase_url, repo_path, branch=branch)
            logger.info(f"Repository cloned succesfully at {repo_path}")
        except GitCommandError:
            raise CloneRepositoryError(f"Failed to clone repository from {codebase_url}")
        return repo_path

    async def clone_local_codebase(self, source_codebase_path):
        source_codebase_path = Path(source_codebase_path)
        if not source_codebase_path.exists():
            logger.error(f"Source codebase directory does not exist: {source_codebase_path} ")
            return None

        repo_name = source_codebase_path.name
        dest_codebase_path = get_codebase_repos_path() / repo_name

        if not create_folder_if_not_exists(dest_codebase_path.parent):
            logger.info(f"{dest_codebase_path.parent} creation already exists")

        if dest_codebase_path.exists():
            logger.info(f"Codebase already exists locally at {dest_codebase_path}. Skipping copying...")

        logger.info(f"Copying local codebase from {source_codebase_path} to {dest_codebase_path}")
        await asyncio.to_thread(shutil.copytree, source_codebase_path, dest_codebase_path)
        logger.info(f"Codebase copied succesfully at {dest_codebase_path}")

    async def clone_local_script(self, script_path: str):
        script_path = get_codebase_script_path()

        script_dest = script_path / Path(script_path).name

        if script_dest.exists():
            logger.info(f"Script already exists locally at {script_dest}. Skipping script copying...")
            return script_dest

        logger.info(f"Copying script from {script_path} to {script_dest}...")
        await asyncio.to_thread(shutil.copy, script_path, script_dest)
        logger.info(f"Script copied succesfully at {script_dest}")
        return script_dest
