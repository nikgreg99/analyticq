import asyncio
import logging
import shutil
from datetime import datetime, timedelta
from threading import Lock

from analyticq.config import AnalyticQBaseConfig
from analyticq.utils import AnalytiCQConfigConst, get_home_analyticq_path

logger = logging.getLogger(__name__)


class CodebaseCleaner:

    _instance = None
    _lock = Lock()

    def _new(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                _instance = super._new__(cls)
        return _instance

    def __init__(self):
        self.base_dir = get_home_analyticq_path()
        codebase_config = AnalyticQBaseConfig.get("codebase")
        self.retention_days = codebase_config["retention"]

    async def cleanup_old_codebase(self):
        retention_period = timedelta(days=self.retention_days)
        for subdir in [AnalytiCQConfigConst.ANALYTICQ_REPOS_FOLDER, AnalytiCQConfigConst.ANALYTICQ_SCRIPTS_FOLDER]:
            dir_path = self.base_dir / subdir
            if dir_path.exists():
                for item in dir_path.iterdir():
                    if item.is_dir():
                        last_modified_period = datetime.fromtimestamp(item.stat().st_mtime)
                        if datetime.now() - last_modified_period > retention_period:
                            logger.info(f"Cleaning up old repository or script: {item}")
                            await asyncio.to_thread(shutil.rmtree, item)
