import logging
from typing import Callable


class ProgressReporter:

    def __init__(self):
        self.progress_callback = []
        self.logger = logging.getLogger(__name__)

    def add_progress_callback(self, callback: Callable[[str, float], None]):
        """
        Adds a progress callback function to the progress reporter.

        The callback function will be called during the execution to report progress updates.

        Args:
            callback (Callable[[str, float], None]): A callback function that takes two parameters:
                - str: A message describing the current progress state
                - float: A number between 0 and 1 indicating the progress percentage

        Returns:
            None
        """
        self.progress_callback.append(callback)

    async def notify_progress(self, message: str, percentage: float):
        """
        Notifies registered callbacks about the progress of an operation.

        This asynchronous method calls all registered progress callbacks with the current progress
        message and percentage. If a callback fails, the error is logged but does not interrupt
        the notification of other callbacks.

        Args:
            message (str): A descriptive message about the current progress state
            percentage (float): The progress percentage between 0.0 and 1.0

        Raises:
            None: Exceptions from callbacks are caught and logged but not re-raised
        """
        for callback in self.progress_callback:
            try:
                callback(message, percentage)
            except Exception as e:
                self.logger.error(f"Progress callback failed: {str(e)}")
