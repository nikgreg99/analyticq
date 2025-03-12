import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from analyticq.preprocessing import CodebaseCleaner


class MockAnalyticQConst:
    ANALYTICQ_REPOS_FOLDER: str = "repos"
    ANALYTICQ_SCRIPTS_FOLDER: str = "scripts"


TEST_BASE_DIR = Path("/fake/home")
RETENTION_DAYS = 30


@pytest.fixture(scope="module")
def setup_cleaner_conf():
    retention_period = timedelta(days=RETENTION_DAYS)

    with patch('analyticq.util.PathUtil', return_value=TEST_BASE_DIR), \
         patch('analyticq.config.AnalyticQBaseConfig.get', return_value={'retention': RETENTION_DAYS}):
        yield TEST_BASE_DIR, retention_period


@pytest.fixture
def codebase_cleaner():
    with patch('analyticq.config.AnalyticQBaseConfig.get') as mock_config:
        mock_config.return_value = {
            "retention": 30
        }
        return CodebaseCleaner()


@pytest.fixture
def mock_scandir_file_not_found():
    with patch("os.scandir", side_effect=FileNotFoundError):
        yield


@pytest.mark.skip(reason="Test is not applicable on Linux due to OS-specific behavior")
def test_get_item_creation_or_last_edit_date(codebase_cleaner):

    with patch("os.path.getctime") as mock_getctime, \
         patch("pathlib.Path.stat") as mock_stat:

        item = MagicMock(spec=Path)
        mock_stat.return_value.st_birthtime = 1609459200  # 2021-01-01 00:00:00
        mock_getctime.return_value = 1609459200

        if os.name == "nt":
            result = codebase_cleaner._get_item_creation_or_last_edit_date(item) == datetime.fromtimestamp(1609459200)
        else:
            mock_stat.return_value.st_mtime = 1609459200  # Set mock modification time
            result = codebase_cleaner._get_item_creation_or_last_edit_date(item) == datetime.fromtimestamp(1609459200)

        assert result is True, f"Expected True based on the sample timestamp used above, got {result}"


def test_is_item_old(codebase_cleaner):
    with patch("analyticq.preprocessing.CodebaseCleaner._get_item_creation_or_last_edit_date") as mock_get_date:
        item = MagicMock(spec=Path)
        mock_get_date.return_value = datetime.now() - timedelta(days=32)
        result = codebase_cleaner._is_item_old(item, timedelta(RETENTION_DAYS))
        assert result is True, f"Expected True for item simulated, got {result}"


def test_is_item_not_old(codebase_cleaner):
    with patch("analyticq.preprocessing.CodebaseCleaner._get_item_creation_or_last_edit_date") as mock_get_date:
        item = MagicMock(spec=Path)
        mock_get_date.return_value = datetime.now() - timedelta(days=10)
        result = codebase_cleaner._is_item_old(item, timedelta(RETENTION_DAYS))
        assert result is False, f"Expected False for item simulated, got {result}"


@pytest.mark.asyncio
async def test_delete_item_dry_run(setup_cleaner_conf):
    codebase_cleaner = CodebaseCleaner()

    with patch("shutil.rmtree") as mock_rmtree, \
         patch("analyticq.preprocessing.input.codebase_cleaner.logger") as mock_logger:
        item = MagicMock(spec=Path)

        await codebase_cleaner._delete_item(item, dry_run=True)
        mock_logger.info.assert_called_with(f"[DRY RUN] Would remove: {item}")
        mock_rmtree.assert_not_called()


@pytest.mark.asyncio
async def test_delete_item_not_dry_run(codebase_cleaner):

    with patch("shutil.rmtree") as mock_rmtree, \
         patch("analyticq.preprocessing.input.codebase_cleaner.logger") as mock_logger:
        item = MagicMock(spec=Path)

        await codebase_cleaner._delete_item(item, dry_run=False)
        mock_logger.info.assert_called_with(f"Successfully removed: {item}")
        mock_rmtree.assert_called_once_with(item)


@pytest.mark.asyncio
async def test_cleanup_old_codebase_with_empty_dir(codebase_cleaner):
    # Set up the instance variables
    codebase_cleaner.base_dir = Path("/mock/path")
    codebase_cleaner.retention_days = 30

    # Mock methods
    codebase_cleaner._is_item_old = MagicMock(return_value=True)
    codebase_cleaner._delete_item = AsyncMock()
    codebase_cleaner._get_item_creation_or_last_edit_date = MagicMock(
        return_value=datetime.now() - timedelta(days=31)
    )

    # Mock items (files and directories)
    mock_item1 = MagicMock(spec=os.DirEntry)
    mock_item1.path = "/mock/path/repos/item1"
    mock_item1.is_dir.return_value = True
    mock_item1.is_file.return_value = False

    # Create a context manager that yields the mock items
    def mock_scandir(dir_path):
        if str(dir_path).endswith("repos"):
            return [mock_item1]
        elif str(dir_path).endswith("scripts"):
            return []
        else:
            return []

    # Patch os.scandir to return a context manager
    with patch("os.scandir", side_effect=lambda x: MagicMock(__enter__=lambda _: mock_scandir(x), __exit__=lambda *_: None)):
        await codebase_cleaner.cleanup_old_codebase(dry_run=True)

        # Assertions
        assert codebase_cleaner._is_item_old.call_count == 1
        assert codebase_cleaner._delete_item.call_count == 1


@pytest.mark.asyncio
async def test_cleanup_old_codebase_with_mixed_items(codebase_cleaner):
    codebase_cleaner.base_dir = Path("/mock/path")
    codebase_cleaner.retention_days = 30

    # Mock items
    mock_old_item = MagicMock(spec=os.DirEntry)
    mock_old_item.path = "/mock/path/repos/old_item"
    mock_old_item.is_dir.return_value = True
    mock_old_item.is_file.return_value = False

    mock_new_item = MagicMock(spec=os.DirEntry)
    mock_new_item.path = "/mock/path/scripts/new_item"
    mock_new_item.is_dir.return_value = False
    mock_new_item.is_file.return_value = True

    # Mock _is_item_old to return True for old items and False for new items
    codebase_cleaner._is_item_old = MagicMock(side_effect=lambda item, _: "old" in str(item))
    codebase_cleaner._delete_item = AsyncMock()

    # Create a context manager that yields the mock items
    def mock_scandir(dir_path):
        if str(dir_path).endswith("repos"):
            return [mock_old_item]
        elif str(dir_path).endswith("scripts"):
            return [mock_new_item]
        else:
            return []

    # Patch os.scandir to return a context manager
    with patch("os.scandir", side_effect=lambda x: MagicMock(__enter__=lambda _: mock_scandir(x), __exit__=lambda *_: None)):
        await codebase_cleaner.cleanup_old_codebase(dry_run=True)

        # Assertions
        assert codebase_cleaner._is_item_old.call_count == 2
        assert codebase_cleaner._delete_item.call_count == 1  # Only the old item is deleted
