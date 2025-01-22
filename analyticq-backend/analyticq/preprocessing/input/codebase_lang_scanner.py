import asyncio
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict

import aiofiles
from analyticq.util import TimeTracker
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

    def __init__(self,
                 metrics_collector: CodebaseMetricsCollector,
                 time_tracker: TimeTracker) -> None:
        if not hasattr(self, "initialized"):
            self.metrics_collector = metrics_collector
            self.time_tracker = time_tracker
            self.max_concurrency = 100
            self.batch_size = 10
            self.semaphore = asyncio.Semaphore(self.max_concurrency)
            self.initialized = True

    async def detect_language(self, file_path: Path) -> str:
        try:
            lexer = get_lexer_for_filename(file_path.name)
            return lexer.name
        except ClassNotFound:
            try:
                async with aiofiles.open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                    content = await f.read()
                    if not content.strip():
                        return "Unknown"
                    lexer = guess_lexer(content)
                    return lexer.name
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
            pass
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
        return "Unknown"

    async def process_file(self, file_path: Path):
        async with self.semaphore:
            try:
                if not FileFilter.is_relevant_file(file_path):
                    size = file_path.stat().st_size
                    self.metrics_collector.add_excluded_file(file_path, size)
                    return

                detected_language = await self.detect_language(file_path)
                size = file_path.stat().st_size
                self.metrics_collector.add_file_statistics(file_path, detected_language, size)

            except FileNotFoundError:
                logger.warning(f"File not found (possibly deleted during scan): {file_path}")
            except PermissionError:
                logger.warning(f"Permission denied when accessing file: {file_path}")
            except OSError as e:
                logger.error(f"OS error while processing file {file_path}: {e}")

    async def process_dir(self, dir_path: Path):
        if not DirFilter.is_relevant_dir(dir_path):
            self.metrics_collector.add_excluded_dir(dir_path)
            return

        try:
            entries = [Path(entry.path) for entry in os.scandir(dir_path) if not DirFilter.is_symlink(entry.path)]

            for i in range(0, len(entries), self.batch_size):
                batch = entries[i : i + self.batch_size]
                tasks = [
                    self.process_file() if entry.is_file() else self.process_dir(entry) for entry in batch
                ]

            await asyncio.gather(*tasks)  # Process tasks concurrently
        except PermissionError:
            logger.warning(f"Permission denied when accessing directory: {dir_path}")
        except FileNotFoundError:
            logger.warning(f"Directory not found (possibly deleted during scan): {dir_path}")
        finally:
            self.time_tracker.update()

    async def scan_codebase_languages(self, root_codebase_path: Path):
        total_files = sum(len(files) for _, _, files in os.walk(root_codebase_path))
        self.time_tracker.start(total_files)

        await self.process_dir(root_codebase_path)

        self.time_tracker.stop()

    def generate_languge_report(self) -> Dict[str, Any]:
        return self.metrics_collector.get_collected_data()
