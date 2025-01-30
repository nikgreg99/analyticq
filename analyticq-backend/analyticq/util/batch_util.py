import logging
import os
from dataclasses import dataclass
from typing import Tuple

import psutil

logger = logging.getLogger(__name__)


@dataclass
class BatchParameters:
    """
    A class to represent the parameters for batch processing.

    Attributes:
    ----------
    batch_size : int
        The size of each batch.
    max_concurrency : int
        The maximum number of concurrent operations.
    load_factor : float
        The load factor for the batch processing.
    """
    batch_size: int
    max_concurrency: int
    load_factor: float


class BatchUtil:
    def __init__(self):
        # Configuration bounds
        self.MIN_BATCH_SIZE = 50
        self.MAX_BATCH_SIZE = 2000
        self.MIN_CONCURRENCY = 1
        self.MEMORY_USAGE_THRESHOLD = 0.25  # 25% of available memory
        self.CPU_USAGE_TARGET = 0.75  # 75% of CPU cores

        # Initialize parameters
        self._current_params = self._initialize_parameters()

    def _initialize_parameters(self) -> BatchParameters:
        """
        This method calculates the optimal batch size and maximum concurrency
        for batch processing by considering the available CPU count and memory.
        It ensures that the batch size and concurrency are within the defined
        minimum and maximum limits.
        Returns:
            BatchParameters: An instance of BatchParameters .
        """
        try:

            cpu_count = os.cpu_count() or 1
            available_memory = psutil.virtual_memory().available

            max_concurrency = max(
                self.MIN_CONCURRENCY,
                int(cpu_count * self.CPU_USAGE_TARGET)
            )

            # Calculate batch size based on available memory
            memory_based_batch = int(
                (available_memory * self.MEMORY_USAGE_THRESHOLD) / (1024 * 1024)
            )
            batch_size = max(
                self.MIN_BATCH_SIZE,
                min(memory_based_batch, self.MAX_BATCH_SIZE)
            )

            params = BatchParameters(
                batch_size=batch_size,
                max_concurrency=max_concurrency,
                load_factor=1.0
            )

            logger.info(
                f"Initialized batch parameters: batch_size={params.batch_size}, "
                f"max_concurrency={params.max_concurrency}"
            )

            return params

        except Exception as e:
            logger.error(f"Error initializing batch parameters: {e}")
            # Return safe default values if initialization fails
            return BatchParameters(
                batch_size=self.MIN_BATCH_SIZE,
                max_concurrency=self.MIN_CONCURRENCY,
                load_factor=1.0
            )

    async def adjust_parameters(self) -> BatchParameters:
        """
        This method retrieves the current CPU and memory usage, calculates a load factor,
        and adjusts the batch size and concurrency accordingly. The adjustments are made
        to ensure optimal performance based on the system's current load.
        Returns:
            BatchParameters: The adjusted batch parameters.
        Raises:
            Exception: If an error occurs during the adjustment process, the current
                       parameters are returned and a warning is logged.
        """
        try:
            # Get current system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Calculate load factors
            cpu_factor = (100 - cpu_percent) / 100
            memory_factor = (100 - memory_percent) / 100

            new_load_factor = min(cpu_factor, memory_factor)
            # Smooth the transition using exponential moving average
            smoothed_load_factor = (
                0.7 * self._current_params.load_factor + 0.3 * new_load_factor
            )

            # Adjust batch size based on load factor
            new_batch_size = int(self._current_params.batch_size * smoothed_load_factor)
            new_batch_size = max(
                self.MIN_BATCH_SIZE,
                min(new_batch_size, self.MAX_BATCH_SIZE)
            )

            # Adjust concurrency based on load factor
            cpu_count = os.cpu_count() or 1
            if smoothed_load_factor < 0.5:
                # Reduce concurrency under high load
                new_concurrency = max(
                    self.MIN_CONCURRENCY,
                    self._current_params.max_concurrency - 1
                )
            elif smoothed_load_factor > 0.8:
                # Increase concurrency under light load
                new_concurrency = min(
                    int(cpu_count * self.CPU_USAGE_TARGET),
                    self._current_params.max_concurrency + 1
                )
            else:
                new_concurrency = self._current_params.max_concurrency

            # Update current parameters
            self._current_params = BatchParameters(
                batch_size=new_batch_size,
                max_concurrency=new_concurrency,
                load_factor=smoothed_load_factor
            )

            logger.debug(
                f"Adjusted parameters: batch_size={new_batch_size}, "
                f"max_concurrency={new_concurrency}, load_factor={smoothed_load_factor:.2f}"
            )
            return self._current_params
        except Exception as e:
            logger.warning(f"Failed to adjust batch parameters: {e}")
            return self._current_params

    @property
    def current_parameters(self) -> BatchParameters:
        """Get current batch parameters."""
        return self._current_params

    def get_batch_ranges(self, total_items: int) -> list[Tuple[int, int]]:
        """
         Calculate batch ranges based on the current batch size.

        Args:
            total_items (int): The total number of items to be processed in batches.

        Returns:
            list[Tuple[int, int]]: A list of tuples where each tuple represents the
            start and end indices of a batch.
        """
        batch_ranges = []
        for start in range(0, total_items, self._current_params.batch_size):
            end = min(start + self._current_params.batch_size, total_items)
            batch_ranges.append((start, end))
        return batch_ranges
