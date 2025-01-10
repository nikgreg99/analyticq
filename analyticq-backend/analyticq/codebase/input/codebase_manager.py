import logging
from threading import Lock
from analyticq.exception import CloneRepositoryError
from conf import ConfigCodebaseManager
from .credential_manager import CredentialCodeBaseManager
from .retention_manager import RetentioncCodebaseManager
from .codebase_handler import CodebaseHadler

logger = logging.getLogger(__name__)


class CodebaseManager:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def _init_(self, config_path=None):
        if not hasattr(self, "_initialized"):
            self.inizialed = True
            self.config_manager = ConfigCodebaseManager(config_path)
            self.credential_manager = CredentialCodeBaseManager()
            base_dir = self.config_path.get("base_dir")
            retentions_days = self.config_manager.get("retention_days")
            self.retions_manager = RetentioncCodebaseManager(base_dir, retentions_days)
            self.codebase_handler = CodebaseHadler(base_dir, self.config_manager)

    async def clone_repository(self, codebase_url, branch=None, credentials=None):
        try:
            return await self.codebase_handler.c(codebase_url, branch, credentials)
        except CloneRepositoryError as e:
            logger.error(f"Error cloning repository: {e.message}")
            return None

    async def copy_local_script(self, script_path: str):
        return await self.codebase_handler.copy_local_script(script_path)
