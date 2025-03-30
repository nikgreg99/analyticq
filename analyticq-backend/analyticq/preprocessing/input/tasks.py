from analyticq.preprocessing import CodebaseCleaner
from celery import shared_task


@shared_task
async def cleanup_old_codebase():
    codebase_cleaner = CodebaseCleaner()
    """
    Asynchronously cleans up old codebase data using the provided CodebaseCleaner instance.

    This function delegates the cleanup operation to the CodebaseCleaner's cleanup_old_codebase method.
    The actual cleanup logic is implemented in the CodebaseCleaner class.

    Args:
        codebase_cleaner (CodebaseCleaner): An instance of CodebaseCleaner that handles the cleanup logic.

    Returns:
        None: This function doesn't return any value.

    Raises:
        Any exceptions that might be raised by the CodebaseCleaner.cleanup_old_codebase method.
    """
    await codebase_cleaner.cleanup_old_codebase()
