import asyncio
import logging
import os
import shutil
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from threading import Lock

from analyticq.config import AnalyticQBaseConfig
from analyticq.util import AnalyticQConst, get_home_AnalyticQ_path

logger = logging.getLogger(__name__)


class CodebaseCleaner:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                _instance = super().__new__(cls)
        return _instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.base_dir = get_home_AnalyticQ_path()
            codebase_config = AnalyticQBaseConfig.get("codebase")
            self.retention_days = codebase_config["retention"]
            self.initialized = True

    @lru_cache(maxsize=1000)
    def _get_item_creation_or_last_edit_date(self, item: Path) -> datetime:
        """
            Get the creation date or the last edit date of a file or a dir

            For Windows it is retrieves the creation path; for UNIX-based system. It retrieves
            the birth time if available, otherwise as fallback to the last modification time

            Args:
                item (Path): The file or directory path

            Returns:
                datetime: Creation or last edit of the target item
        """
        try:
            if os.name == "nt":
                return datetime.fromtimestamp(os.path.getctime(item))
            else:  # UNIX-Based System
                stat = item.stat()
                return datetime.fromtimestamp(stat.st_birthtime)  # May arise AttributeError
        except (AttributeError, OSError):
            return datetime.fromtimestamp(item.stat().st_mtime)

    def _is_item_old(self, item: Path, retention_period: timedelta) -> bool:
        """
            Checks if a file or a directory is older than retention period

            Args:
                item (Path): The target file or dir path

            Returns:
                bool: True if the item is older than retention period, False otherwise

        """
        creation_date = self._get_item_creation_or_last_edit_date(item)
        return datetime.now() - creation_date > retention_period

    async def _delete_item(self, item: Path, dry_run: bool) -> None:
        """
         Delete a given item asynchroniously

        if 'dry_run' is True, it simulates the deletion by logging what would have been deleted.
        Otherwise, it attempts to execute the operation logging its outcome.

         Args:
            item (Path): The target file for dir path
            dry_run (bool): Flags that logs only the deletion without effecttively deleting the item

        """
        if dry_run:
            logger.info(f"[DRY RUN] Would remove: {item}")
        else:
            try:
                await asyncio.to_thread(shutil.rmtree, item)
                logger.info(f"Successfully removed: {item}")
            except Exception:
                logger.error(f"Failed to remove {item}")

    async def cleanup_old_codebase(self, dry_run: bool = False) -> None:
        """
        Cleans up old codebase files (repositories and scripts) that are older than the specifie
        retention period.

        This method checks all files within the repositories and scripts directories. If a file or
        directory is older than the retention period, it is deleted. If `dry_run` is True, it
        only simulates the deletion.

        Args:
            dry_run (bool): If True, it simulates the cleanup without actually deleting items.

        """
        retention_period = timedelta(days=self.retention_days)
        for subdir in [
            AnalyticQConst.ANALYTICQ_REPOS_FOLDER,
            AnalyticQConst.ANALYTICQ_SCRIPTS_FOLDER
        ]:
            dir_path = self.base_dir / subdir
            if dir_path.exists():
                for item in dir_path.iterdir():
                    if self._is_item_old(item, retention_period):
                        await self._delete_item(item, dry_run)
