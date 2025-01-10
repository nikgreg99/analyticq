import asyncio
import logging
import shutil
from pathlib import Path
from threading import Lock
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RetentioncCodebaseManager:

    _instance = None
    _lock = Lock()

    def _new(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                _instance = super._new__(cls)
        return _instance

    def __init__(self, base_dir: str, retention_days: int = 15):
        self.base_dir = Path(base_dir)
        self.retention_days = retention_days

    async def cleanup_old_codebases(self):
        retention_period = timedelta(days=self.retention_days)
        for subdir in ['repositories', 'scripts']:
            dir_path = self.base_dir / subdir
            if dir_path.exists():
                for item in dir_path.iterdir():
                    if item.is_dir():
                        last_modified_period = datetime.fromtimestamp(item.stat().st_mtime)
                        if datetime.now() - last_modified_period > retention_period:
                            logger.info(f"Cleaning up old repository or script: {item}")
                            await asyncio.to_thread(shutil.rmtree, item)
