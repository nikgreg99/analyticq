import time
from datetime import datetime, timezone


def get_unix_time() -> int:
    """
         Returns the current Unix time.
    """
    return int(time.time())


def get_timestamp() -> str:
    """
         Returns the current timestamp.
    """
    current_time = datetime.now()
    return current_time.strftime("%Y-%m-%d %H:%M:%S") + f".{current_time.microsecond // 1000:03d}"


def parse_unix_timestamp(unix_timestamp) -> str:
    """
    Converts a Unix timestamp to a human-readable date-time string in 'YYYY-MM-DD HH:MM:SS' format.

    Args:
        unix_timestamp (int): The Unix timestamp to be parsed.

    Returns:
        str: The formatted date-time string.
    """
    dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return dt.strftime(unix_timestamp).strftime("%Y-%m-%d %H:%M:%S")
