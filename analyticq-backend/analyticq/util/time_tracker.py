import logging
import time
from typing import Optional

from tqdm import tqdm

logger = logging.getLogger(__name__)


class TimeTrackerUtils:

    def __init__(self):
        self.progress_bar: Optional[tqdm] = None
        self.start_time: Optional[float] = None
        self.total_files: int = 0

    def start(self, total_files: int) -> None:
        """
        Initializes the time tracker and starts the progress bar.

        Args:
            total_files (int): The total number of files to be processed. Must be greater than 0.

        Raises:
            ValueError: If the total_files is less than or equal to 0.

        Initializes:
            self.total_files (int): Stores the total number of files.
            self.start_time (float): Stores the start time of the process.
            self.progress_bar (tqdm): Initializes the progress bar with the total number of files.
        """
        if self.progress_bar:
            self.progress_bar.close()
        self.total_files = total_files
        if total_files <= 0:
            raise ValueError("Total files must be greate than 0.")
        self.start_time = time.time()
        self.progress_bar = tqdm(
            total=total_files,
            desc="🔍 Scanning Codebase",
            unit="file",
            dynamic_ncols=True
        )

    def update(self, count: int = 1) -> None:
        """
        Updates the progress bar and calculates the estimated time remaining.

        Args:
            count (int, optional): The number of increments to update the progress bar by. Defaults to 1.

        Returns:
            None

        Raises:
            ZeroDivisionError: If there is an attempt to divide by zero when calculating progression.
            ValueError: If there is an invalid value encountered during calculations.

        Notes:
            - If the progress bar is not initialized or the start time is not set, the method will not proceed.
            - The method calculates the elapsed time since the start and uses it to estimate the total time required and the remaining time.
            - The progress bar is updated with the estimated time remaining (ETA) and the processing speed (files per second).
        """
        if self.progress_bar and self.start_time:
            self.progress_bar.update(count)

        elapsed_time = time.time() - self.start_time
        if elapsed_time <= 0:
            return

        try:
            progression = self.progress_bar.n / self.total_files

            estimated_total_time = elapsed_time / progression if progression > 0 else float('inf')
            estimated_time_remaining = estimated_total_time - elapsed_time
            processing_speed = self.progress_bar.n / elapsed_time if elapsed_time > 0 else 0.0
            self.progress_bar.set_postfix(
                ETA=f"{estimated_time_remaining:.2f}s",
                Speed=f"{processing_speed:.2f} files/s"
            )

        except (ZeroDivisionError, ValueError) as ex:
            logger.warning(f"Failed to calculate estimated time remaining: {ex}")

    def stop(self):
        """
        Stops the time tracker and logs the elapsed time.

        If a progress bar is being used, it will be closed. The elapsed time
        since the start of the time tracker will be calculated and logged.

        Raises:
            AttributeError: If 'start_time' is not set before calling this method.
        """
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        elapsed_time = time.time() - self.start_time
        logger.info(f"\n✅ Scan completed in {elapsed_time:.2f} seconds.")

    @property
    def progress(self) -> bool:
        """
        Calculate the progress percentage of the progress bar.

        Returns:
            bool: The progress percentage as a float value between 0.0 and 100.0.
                  Returns 0.0 if the progress bar is not initialized or if the total number of files is zero.
        """
        if not self.progress_bar or self.total_files == 0:
            return 0.0
        return (self.progress_bar.n / self.total_files) * 100

    @property
    def elapsed_time(self) -> float:
        """
        Calculate the elapsed time since the start time.

        Returns:
            float: The elapsed time in seconds. If the start time is not set, returns 0.0.
        """
        if not self.start_time:
            return 0.0
        return time.time() - self.start_time
