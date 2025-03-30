import asyncio
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from analyticq.preprocessing.filter import DirFilter, FileFilter
from analyticq.preprocessing.metric import CodebaseMetricsReporter
from analyticq.util import (BatchParameters, BatchUtil, FileUtil,
                            TimeTrackerUtils)
from dependency_injector.wiring import Provide, inject
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)


class CodebaseLangScanner:
    """
    A class responsible for scanning and analyzing a codebase to detect programming languages and collect metrics.

    This class provides functionality to:
    - Detect programming languages of files
    - Count lines of code
    - Process files in batches
    - Generate codebase metrics reports

    The scanner uses multiple detection methods and handles various edge cases while processing files.
    It implements batch processing with controlled concurrency for better performance.

    Attributes:
        metrics_reporter (CodebaseMetricsReporter): Reporter for collecting and storing codebase metrics
        time_tracker (TimeTrackerUtils): Utility for tracking processing time and progress
        batch_util (BatchUtil): Utility for managing batch processing parameters

    Dependencies:
        - pygments for language detection
        - asyncio for concurrent processing
        - dependency injection framework

    Example:
        ```python
        scanner = CodebaseLangScanner()
        await scanner.scan_codebase(Path("/path/to/codebase"))
        report = scanner.generate_codebase_report()
        ```

        The class  implementsvarious filtering mechanisms to exclude irrelevant files and directories.
    """
    @inject
    def __init__(self,
                 metrics_reporter: Provide[CodebaseMetricsReporter],
                 time_tracker: Provide[TimeTrackerUtils],
                 batch_util: Provide[BatchUtil]) -> None:

        if not hasattr(self, "_initialized"):
            self.metrics_reporter = metrics_reporter
            self.time_tracker = time_tracker
            self.batch_util = batch_util
            self._initialized = True

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
        """
        Attempts to detect the programming language of a file using multiple methods.
        This method follows a two-step approach:
        1. Attempts to detect language based on file extension/name
        2. If that fails, attempts to detect based on file content

        Args:
            file_path (Path): Path object pointing to the file to analyze

        Returns:
            str: Detected programming language name, or "Unknown" if detection fails
            int: Returns 0 along with "Unknown" in case of failure

        Raises:
            ClassNotFound: If lexer class is not found for the file
            Exception: For any other errors during language detection

        Note:
            The detection is performed using Pygments lexers. The accuracy depends on
            both the file extension and content patterns.
        """
        try:
            # First attempt: detect by filename
            lexer = get_lexer_for_filename(file_path.name)
            return lexer.name
        except ClassNotFound:
            logger.warning(f"No lexer got the given filename  was not found {file_path.name}. Try detecting file type by content")
        except Exception:
            logger.warning(f"Unknown error occuer for guessing fie content for {file_path.name}. Try detecting file type by content")

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

    async def analyze_file(self, file_path: Path, file_group: defaultdict):
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
                self.metrics_reporter.add_excluded_file(file_path, size)
                return

            language, loc = await self.detect_language_and_loc(file_path)
            size = file_path.stat().st_size
            self.metrics_reporter.add_file_statistics(file_path, language, size, loc)

            file_group[language].append(file_path)

        except FileNotFoundError:
            logger.warning(f"File not found (possibly deleted during scan): {file_path}")
        except PermissionError:
            logger.warning(f"Permission denied while accessing file: {file_path}")
        except OSError as e:
            logger.error(f"OS error while processing file {file_path}: {e}")

    async def _process_files_batch(self, files: List[Path], file_group: defaultdict, params: BatchParameters) -> None:
        """
        Process a batch of files concurrently with controlled concurrency.
        This method handles concurrent processing of multiple files using asyncio, with a semaphore
        to control the maximum number of concurrent operations.
        Args:
            files (List[Path]): List of file paths to process
            file_group (defaultdict): Dictionary to store file processing results
            params (BatchParameters): Parameters for batch processing containing max_concurrency
        Returns:
            None
        Note:
            - Uses asyncio.Semaphore to limit concurrent operations
            - Handles file processing concurrently via asyncio.gather
            - Allows exceptions to be returned rather than raised (return_exceptions=True)
        """

        sem = asyncio.Semaphore(params.max_concurrency)

        async def process_with_semaphore(file_path: Path) -> None:
            async with sem:
                await self.analyze_file(file_path, file_group)

        await asyncio.gather(
            *[process_with_semaphore(file_path) for file_path in files],
            return_exceptions=True
        )

    async def _process_files(self, files: List[Path], file_groups: defaultdict) -> None:
        """
        Process a list of files in batches, updating file groups with language information.

        This method handles the batch processing of files by splitting them into smaller chunks
        and processing each batch separately while dynamically adjusting processing parameters.

        Args:
            files (List[Path]): List of Path objects representing files to be processed
            file_groups (defaultdict): Dictionary to store files grouped by their language

        Returns:
            None

        Note:
            This method works asynchronously and uses batch processing for better performance
            and resource management. The batch parameters are automatically adjusted based on
            system performance and load.
        """
        params = await self.batch_util.adjust_parameters()
        batch_ranges = self.batch_util.get_batch_ranges(len(files))

        for start, end in batch_ranges:
            batch = files[start:end]
            await self._process_files_batch(batch, file_groups, params)
            params = await self.batch_util.adjust_parameters()

    async def process_directory(self, dir_path: Path, file_groups: defaultdict):
        """
        Recursively processes a directory to analyze files and subdirectories.

        This method scans the given directory path, processes files in batches, and recursively handles subdirectories.
        It skips irrelevant directories and handles symlinks according to configuration.

        Args:
            dir_path (Path): Path object representing the directory to process
            file_groups (defaultdict): Dictionary to store processed files grouped by some criteria

        Returns:
            None

        Raises:
            PermissionError: If access to directory is denied
            FileNotFoundError: If directory no longer exists during processing

        Notes:
            - Uses batch processing for files to optimize performance
            - Skips symlinks and irrelevant directories
            - Updates metrics for excluded directories
            - Tracks processing time
        """

        if DirFilter.is_irrelevant_dir(dir_path):
            self.metrics_reporter.add_excluded_dir(dir_path)
            return

        try:
            entries = [Path(entry.path) for entry in os.scandir(dir_path)]
            files = [entry for entry in entries if entry.is_file()]
            directories = [entry for entry in entries if entry.is_dir()]

            if files:
                await self._process_files(files, file_groups)

            for directory in directories:
                await self.process_directory(directory, file_groups)

        except PermissionError:
            logger.warning(f"Permission denied while accessing directory: {dir_path}")
        except FileNotFoundError:
            logger.warning(f"Directory not found (possibly deleted during scan): {dir_path}")
        finally:
            self.time_tracker.update()

    async def scan_codebase(self, root_codebase_path: Path) -> None:
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

        await self.process_directory(root_codebase_path, file_groups)
        self.time_tracker.stop()

    def generate_codebase_report(self) -> Dict[str, Any]:
        """
        Generates a comprehensive report containing metrics about the codebase.
        Returns
        -------
        Dict[str, Any]
        A dictionary containing various metrics about the codebase, including:
            - Language distribution
            - File counts
            - Code statistics
            - And other relevant codebase metrics collected by the metrics reporter
    """
        return self.metrics_reporter.get_codebase_metric_report()
