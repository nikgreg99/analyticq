import asyncio
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict

import aiofiles
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.util import ClassNotFound

from ..filter.dir_filter import DirFilter
from ..filter.file_filter import FileFilter
from ..metric.metric_collector import CodebaseMetricsCollector

logger = logging.getLogger(__name__)


class CodebaseLangScanner:

    _instance = None
    _lock = Lock()

    def __new__(cls, *arg, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr("initialized"):
            self.metrics_collector = CodebaseMetricsCollector()
            self.initizalied = True

    async def detect_language(self, file_path: Path) -> str:
        try:
            lexer = get_lexer_for_filename(file_path.name)
            return lexer.name
        except ClassNotFound:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                content = await f.read()
                lexer = guess_lexer(content)
                return lexer.name
        except Exception:
            pass
        return "Unknown"

    async def process_file(self, file_path: Path):
        if not FileFilter.is_relevant_file(file_path):
            size = file_path.stat().st_size
            self.metrics_collector.add_excluded_file(file_path, size)
            return

        detected_language = await self.detect_language(file_path)
        size = file_path.stat().st_size
        self.metrics_collector.add_file_statistics(file_path, detected_language, size)

    async def process_dir(self, dir_path: Path):
        if not DirFilter.is_relevant_dir(dir_path):
            self.metrics_collector.add_excluded_dir(dir_path)
            return

        tasks = []
        for entry in os.scandir(dir_path):
            entry_path = Path(entry.path)
            if entry_path.is_file():
                tasks.append(self.process_file(entry_path))
            elif entry_path.is_dir():
                tasks.append(self.process_dir(entry_path))

        await asyncio.gather(*tasks)

    async def scan_codebase_languages(self, root_codebase_path: Path):
        await self.process_dir(root_codebase_path)

    def generate_languge_report(self) -> Dict[str, Any]:
        return self.metrics_collector.get_metrics_report()
