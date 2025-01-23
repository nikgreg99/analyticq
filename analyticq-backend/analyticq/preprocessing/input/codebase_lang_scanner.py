import asyncio
import logging
import os
from collections import defaultdict
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List

import aiofiles
from analyticq.util import ResourceUtil, TimeTrackerUtils
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
                 time_tracker: TimeTrackerUtils) -> None:
        if not hasattr(self, "initialized"):
            self.metrics_collector = metrics_collector
            self.time_tracker = time_tracker
            self.max_concurrency = ResourceUtil.max_workers_available()
            self.batch_size = ResourceUtil.max_batch_size_available()
            asyncio.Semaphore(self.max_concurrency)
            self.initialized = True

    async def detect_language_and_loc(self, file_path: Path):
        try:
            lexer = get_lexer_for_filename(file_path.name)
            language = lexer.name
        except ClassNotFound:
            try:
                async with aiofiles.open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                    content = await f.read()
                    if not content.strip():
                        return "Unknown", 0
                    lexer = guess_lexer(content)
                    language == lexer.name
                    loc = len(content.splitlines())
                    return language, loc
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
        return "Unknown", 0

    async def process_file(self, file_path: Path, file_group: defaultdict):
        try:
            if not FileFilter.is_relevant_file(file_path):
                size = file_path.stat().st_size
                self.metrics_collector.add_excluded_file(file_path, size)
                return

            detected_language, loc = await self.detect_language_and_loc(file_path)
            size = file_path.stat().st_size
            self.metrics_collector.add_file_statistics(file_path, detected_language, size, loc)

            file_group[detected_language].append(file_path)

        except FileNotFoundError:
            logger.warning(f"File not found (possibly deleted during scan): {file_path}")
        except PermissionError:
            logger.warning(f"Permission denied when accessing file: {file_path}")
        except OSError as e:
            logger.error(f"OS error while processing file {file_path}: {e}")

    async def batch_process_files(self, language: str, files: List[Path]):
        """Batch process files for a given language with concurrency control."""
        file_batches = [files[i:i + self.batch_size] for i in range(0, len(files), self.batch_size)]

        for batch in file_batches:
            tasks = []
            for file_path in batch:
                tasks.append(self.process_file(file_path, language))

            # Control concurrency for each batch
            async with asyncio.Semaphore(self.batch_concurrency):
                await asyncio.gather(*tasks)

    async def process_dir(self, dir_path: Path, file_group: defaultdict):

        if not DirFilter.is_relevant_dir(dir_path):
            self.metrics_collector.add_excluded_dir(dir_path)
            return

        try:
            entries = [Path(entry.path) for entry in os.scandir(dir_path) if not DirFilter.is_symlink(entry.path)]

            tasks = []
            for entry in entries:
                if entry.is_file():
                    tasks.append(self.process_file(entry, file_group))
                else:
                    tasks.append(self.process_dir(entry, file_group))

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

        file_groups = defaultdict(list)

        await self.process_dir(root_codebase_path, file_groups)

        tasks = []
        # Once all files are grouped, process them in parallel
        for language, files in file_groups.items():
            tasks.append(self.batch_process_files(language, files))

        await asyncio.gather(*tasks)

        self.time_tracker.stop()

    def generate_languge_report(self) -> Dict[str, Any]:
        return self.metrics_collector.get_collected_data()
