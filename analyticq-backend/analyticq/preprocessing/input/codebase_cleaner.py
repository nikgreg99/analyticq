import asyncio
import logging
import os
import shutil
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from threading import Lock

from analyticq.config import AnalyticQBaseConfig
from analyticq.util import AnalyticQConst, PathUtil

logger = logging.getLogger(__name__)


class CodebaseCleaner:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.base_dir = PathUtil.get_home_AnalyticQ_path()
            codebase_config = AnalyticQBaseConfig.get("codebase")
            self.retention_days = codebase_config["retention"]
            self._initialized = True

    def _initialize(self):
        """
        Initialize the CodebaseCleaner with configuration settings.
        This method sets up the base directory for AnalyticQ and retrieves the retention period
        from the configuration. It performs validation to ensure the retention period is valid.
        Raises:
            ValueError: If retention_days is not a non-negative integer.
        """
        self.base_dir = PathUtil.get_home_AnalyticQ_path()
        codebase_config = AnalyticQBaseConfig.get("codebase")
        self.retention_days = codebase_config["retention"]

        if not isinstance(self.retention_days, int) or self.retention_days < 0:
            raise ValueError("retention_days must be a non-negative integer")

        self._initialized = True

    @lru_cache(maxsize=1000)
    def _get_item_creation_or_last_edit_date(self, item: Path) -> datetime:
        """
            Get the creation date or the last edit date of a file or a dir

            For Windows it is retrieves the creation path; for UNIX-based system it retrieves
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
            except OSError as e:
                logger.error(f"Failed to remove {item}: {e}", exc_info=True)

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
            if not dir_path.exists():
                logger.warning(f"Directory does not exist: {dir_path}")
                continue

            with os.scandir(dir_path) as it:
                for entry in it:
                    item = Path(entry.path)
                    if self._is_item_old(item, retention_period):
                        await self._delete_item(item, dry_run)
