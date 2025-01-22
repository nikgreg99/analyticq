import logging
import time

from tqdm.asyncio import tqdm

logger = logging.getLogger(__name__)


class TimeTracker:

    def __init__(self):
        self.progress_bar = None
        self.start_time = None
        self.total_files = 0

    def start(self, total_files: int):
        self.total_files = total_files
        self.start_time = time.time()
        self.progress_bar = tqdm(
            total=total_files,
            desc="🔍 Scanning Codebase",
            unit="file",
            dynamic_ncols=True
        )

    def update(self, count: int = 1):
        if self.progress_bar:
            self.progress_bar.update(count)

        elapsed_time = time.time() - self.start_time
        progression = self.progress_bar.n / self.total_files

        if progression > 0:
            estimated_total_time = elapsed_time / progression
            estimated_time_remaining = estimated_total_time - elapsed_time
            self.progress_bar.set_postfix(
                ETA=f"{estimated_time_remaining:2.f}s",
                Speed=f"{self.progress_bar.n / elapsed_time:.2f} files/s"
            )

    def stop(self):
        if self.progress_bar:
            self.progress_bar.close()
        elapsed_time = time.time() - self.start_time()
        logger.info(f"\n✅ Scan completed in {elapsed_time:.2f} seconds.")
