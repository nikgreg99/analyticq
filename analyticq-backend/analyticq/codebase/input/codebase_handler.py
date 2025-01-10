import asyncio
import logging
import shutil
from pathlib import Path
from enum import Enum
from urllib.parse import urlparse
from threading import Lock
from git import Repo, GitCommandError
from analyticq.exception import CloneRepositoryError

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

    async def clone_codebase(self, codebase_url: str, branch: str = None, credentials: str = None):
        protocol = self._get_protocol(codebase_url)
        repo_name = codebase_url.split("/")[-1].replace(".git", "")
        repo_path = self.base_dir / "repositories" / repo_name
        repo_path.parent.mkdir(exist_ok=True)

        if repo_path.exists():
            logger.info(f"Codebase already exists locally at {repo_path}. Skipping cloning...")
            return repo_path

        branch = branch or self.config_manager.get("default_branch", "main")
        logger.info(f"Cloning codebase from {codebase_url} at branch {branch} using protocol {protocol}...")

        if credentials and credentials.auth_token:
            codebase_url = codebase_url.replace("https://", f"https://{credentials.auth_token}@")
        try:
            await asyncio.to_thread(Repo.clone, codebase_url, repo_path, branch=branch)
        except GitCommandError as e:
            codebase_error_message = f"Failed to clone repository from {codebase_url}. Error: {e._msg}"
            logger.info(f"Repository cloned succesfully at {repo_path}")
            raise CloneRepositoryError(codebase_error_message)
        return repo_path

    async def copy_local_script(self, script_path: str):
        script_path = self.base_dir / "scripts"
        script_path.mkdir(exist_ok=True)

        script_dest = script_path / Path(script_path).name

        if script_dest.exists():
            logger.info(f"Script already exists locally at {script_dest}. Skipping copying...")
            return script_dest

        logger.info(f"Copying script from {script_path} to {script_dest}...")
        await asyncio.to_thread(shutil.copy, script_path, script_dest)
        logger.info(f"Script copied succesfully at {script_dest}")
        return script_dest
