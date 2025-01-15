import asyncio
import logging
import os
import shutil
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from threading import Lock

from analyticq.config import AnalyticQBaseConfig
from analyticq.utils import AnalytiCQConfigConst, get_home_analyticq_path

logger = logging.getLogger(__name__)


class CodebaseCleaner:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                _instance = super._new__(cls)
        return _instance

    def __init__(self):
        self.base_dir = get_home_analyticq_path()
        codebase_config = AnalyticQBaseConfig.get("codebase")
        self.retention_days = codebase_config.get("retention", 30)

    @lru_cache(maxsize=1000)
    def _get_item_creation_or_last_edit_date(self, item: Path) -> datetime:
        try:
            if os.name == "nt":
                return datetime.fromtimestamp(os.path.getctime(item))
            else:  # UNIX-Based System
                stat = item.stat()
                return datetime.fromtimestamp(stat.st_birthtime)  # May arise AttributeError
        except (AttributeError, OSError):
            return datetime.fromtimestamp(item.stat().st_mtime)

    def _is_item_old(self, item: Path, retention_period: timedelta) -> bool:
        creation_date = self._get_item_creation_or_last_edit_date(item)
        return datetime.now() - creation_date > retention_period

    async def _delete_item(self, item: Path, dry_run: bool):
        if dry_run:
            logger.info(f"[DRY RUN] Would remove: {item}")
        else:
            try:
                asyncio.to_thread(shutil.rmtree, item)
                logger.info(f"Successfully removed: {item}")
            except Exception:
                logger.error(f"Failed to remove {item}")

    async def cleanup_old_codebase(self, dry_run: bool = False):
        retention_period = timedelta(days=self.retention_days)
        for subdir in [
            AnalytiCQConfigConst.ANALYTICQ_REPOS_FOLDER,
            AnalytiCQConfigConst.ANALYTICQ_SCRIPTS_FOLDER
        ]:
            dir_path = self.base_dir / subdir
            if dir_path.exists():
                for item in dir_path.iterdir():
                    if item.is_dir() and self._is_item_old(item, retention_period):
                        await self._delete_item(item, dry_run)
