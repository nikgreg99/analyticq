import logging
from threading import Lock

from .cloner import InputCloner
from .codebase_cleaner import CodebaseCleaner
from .credential_manager import CredentialCodeBaseManager

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
            self.credential_manager = CredentialCodeBaseManager()
            self.codebase_cleaner = CodebaseCleaner()
            self.codebase_cloner = InputCloner()

    async def clone_remote_codebase(self, codebase_url, branch=None, credentials=None):
        await self.codebase_cloner.clone_remote_codebase(codebase_url, branch, credentials)

    async def clone_local_codebase(self, codebase_path):
        await self.codebase_cloner.clone_local_codebase(codebase_path)

    async def copy_local_script(self, script_path: str):
        await self.codebase_cloner.clone_local_script(script_path)

    async def cleanup_old_codebase(self):
        await self.codebase_cleaner.cleanup_old_codebase()
