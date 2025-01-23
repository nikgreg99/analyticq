import os

import psutil

from .const import AnalyticQConst


class ResourceUtil:

    @staticmethod
    def max_workers_available(cpu_itensive: bool = True):
        cpu_cores = os.cpu_count() or 2
        cpu_load = psutil.cpu_percent(interval=0.5)  # Check CPU load

        if cpu_itensive:
            max_workers = max(2, cpu_cores // 2)  # Fewer workers for CPU-heavy tasks
        else:
            max_workers = min(2 * cpu_cores, 16)  # More workers for I/O-heavy tasks)

        if cpu_load > AnalyticQConst.DEFAULT_CPU_LOAD_THRESHOLD:
            max_workers = max(2, max_workers // 2)

        return max_workers

    @staticmethod
    def max_batch_size_available(total_files: int , avg_file_size_kb: int):
        memory = psutil.virtual_memory()

        if total_files < 1000:
            return 100
        elif memory.available > 8 * 1024 ** 3:  # If 8GB are free
            return min(5000, max(1000, (memory.available // (avg_file_size_kb * 1024)) // 10))  # This ensure batch size scales with the available mmeory
        else:
            return AnalyticQConst.DEFAULT_BATCH_SIZE_THRESHOLD  # Default batch size
