import asyncio
import logging
import os
from collections import defaultdict
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Tuple

from analyticq.preprocessing.filter.dir_filter import DirFilter
from analyticq.preprocessing.filter.file_filter import FileFilter
from analyticq.preprocessing.metric.metric_collector import \
    CodebaseMetricsCollector
from analyticq.util import (BatchParameters, BatchUtil, FileUtil,
                            TimeTrackerUtils)
from dependency_injector.wiring import Provide, inject
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)


class CodebaseLangScanner:

    _instance = None
    _lock = Lock()

    def __new__(cls, *arg, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    @inject
    def __init__(self,
                 metrics_collector: Provide[CodebaseMetricsCollector],
                 time_tracker: Provide[TimeTrackerUtils],
                 batch_util: Provide[BatchUtil]) -> None:
        if not hasattr(self, "initialized"):
            self.metrics_collector = metrics_collector
            self.time_tracker = time_tracker
            self.batch_util = batch_util
            self.initialized = True

    async def detect_language_and_loc(self, file_path: Path) -> Tuple[str, int]:
        """
        Detects the programming language and lines of code (LOC) of a given file.

        Args:
            file_path (Path): The path to the file to be analyzed.

        Returns:
            Tuple[str, str]: A tuple containing the detected programming language and the number of lines of code.
                             If the language cannot be detected, returns ("Unknown", 0).

        Raises:
            Exception: If an error occurs during language detection or LOC counting, logs the error and returns ("Unknown", 0).
        """
        try:
            language = await self._detect_language(file_path)
            loc = await FileUtil.count_lines(file_path) if language != "Unknown" else 0
            return language, loc
        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return "Unknown", 0

    async def _detect_language(self, file_path: Path) -> str:
        """Attempts to detect the programming language of the file."""
        try:
            # First attempt: detect by filename
            lexer = get_lexer_for_filename(file_path.name)
            return lexer.name
        except ClassNotFound:
            pass

        # Second attempt: detect by content
        try:
            content = await FileUtil.read_file_content(file_path)
            if not content.strip():
                return "Unknown", 0
            lexer = guess_lexer(content)
            return lexer.name
        except Exception as e:
            logger.warning(f"Failed to detect language by content for {file_path}: {e}")
            return "Unknown", 0

    async def process_file(self, file_path: Path, file_group: defaultdict):
        """
        Process a single file in the codebase to detect its programming language and collect metrics.

        This method analyzes the given file, determines its programming language, counts lines of code,
        and collects various metrics like file size. The results are stored in the metrics collector
        and the file is grouped by its detected language.

        Args:
            file_path (Path): Path object pointing to the file to be processed
            file_group (defaultdict): Dictionary to group files by their detected programming language

        Returns:
            None

        Raises:
            FileNotFoundError: If the target file does not exist or was deleted during processing
            PermissionError: If there are insufficient permissions to access the file
            OSError: If an operating system level error occurs while processing the file

        """
        try:
            # File not relevant are discarded
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

    async def process_files_batch(self, files: List[Path], file_group: defaultdict, params: BatchParameters) -> None:
        """Process a batch of files concurrently with controlled concurrency."""
        sem = asyncio.Semaphore(params.max_concurrency)

        async def process_with_semaphore(file_path: Path) -> None:
            async with sem:
                await self.process_file(file_path, file_group)

        await asyncio.gather(
            *[process_with_semaphore(file_path) for file_path in files],
            return_exceptions=True
        )

    async def process_dir(self, dir_path: Path, file_groups: defaultdict):

        if not DirFilter.is_relevant_dir(dir_path):
            self.metrics_collector.add_excluded_dir(dir_path)
            return

        try:
            entries = [
                Path(entry.path)
                for entry in os.scandir(dir_path)
                if not DirFilter.is_symlink(entry)]
            files = [entry for entry in entries if entry.is_file()]
            directories = [entry for entry in entries if entry.is_dir()]
            if files:
                params = await self.batch_util.adjust_parameters()
                batch_ranges = self.batch_util.get_batch_ranges(len(files))
                for start, end in batch_ranges:
                    batch = files[start:end]
                    await self.process_files_batch(batch, file_groups, params)
                    params = await self.batch_util.adjust_parameters()

                for directory in directories:
                    await self.process_dir(directory, file_groups)

        except PermissionError:
            logger.warning(f"Permission denied when accessing directory: {dir_path}")
        except FileNotFoundError:
            logger.warning(f"Directory not found (possibly deleted during scan): {dir_path}")
        finally:
            self.time_tracker.update()

    async def scan_codebase_languages(self, root_codebase_path: Path) -> None:
        """
        Scans the codebase to identify and categorize files based on their programming languages.

        This method recursively traverses the codebase directory, processes each file, and groups
        them according to their detected programming language. It tracks the processing time and
        progress using a time tracker.

        Args:
            root_codebase_path (Path): The root directory path of the codebase to be scanned.


        Note:
            The method uses an internal time tracker to monitor progress and performance.
            Results are stored internally in the file groups data structure.
        """
        total_files = sum(len(files) for _, _, files in os.walk(root_codebase_path))
        self.time_tracker.start(total_files)
        file_groups = defaultdict(list)

        await self.process_dir(root_codebase_path, file_groups)

        self.time_tracker.stop()

    def generate_languge_report(self) -> Dict[str, Any]:
        """
        Generates a report of the programming language metrics collected during scanning.

        Returns:
            Dict[str, Any]: A dictionary containing the collected language metrics data with:
                - File counts by extension
                - Line counts by language
                - Other language-specific statistics
        """
        return self.metrics_collector.get_collected_data()
