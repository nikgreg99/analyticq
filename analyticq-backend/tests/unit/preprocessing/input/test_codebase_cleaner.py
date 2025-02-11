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
async def test_cleanup_old_codebase_basic(codebase_cleaner):
    # Set up the instance variables
    codebase_cleaner.base_dir = Path("/mock/path")
    codebase_cleaner.retention_days = 30

    codebase_cleaner._is_item_old = MagicMock(return_value=True)
    codebase_cleaner._delete_item = AsyncMock()
    codebase_cleaner._get_item_creation_or_last_edit_date = MagicMock(return_value=datetime.now() - timedelta(days=31))

    mock_item1 = MagicMock(spec=Path)
    mock_item1.is_dir.return_value = True
    mock_item1.is_file.return_value = False

    mock_item2 = MagicMock(spec=Path)
    mock_item2.is_dir.return_value = False
    mock_item2.is_file.return_value = True

    with patch.object(Path, "exists", return_value=True), \
         patch.object(Path, "iterdir", return_value=[mock_item1, mock_item2]), \
         patch("analyticq.util.AnalyticQConst", MockAnalyticQConst):

        await codebase_cleaner.cleanup_old_codebase(dry_run=True)

        assert codebase_cleaner._is_item_old.call_count == 4
        assert codebase_cleaner._delete_item.call_count == 4


@pytest.mark.asyncio
async def test_cleanup_old_codebase_with_empty_dir(codebase_cleaner):
    # Set up the instance variables
    codebase_cleaner.base_dir = Path("/mock/path")
    codebase_cleaner.retention_days = 30

    codebase_cleaner._is_item_old = MagicMock(return_value=True)
    codebase_cleaner._delete_item = AsyncMock()
    codebase_cleaner._get_item_creation_or_last_edit_date = MagicMock(return_value=datetime.now() - timedelta(days=31))

    mock_item1 = MagicMock(spec=Path)
    mock_item1.is_dir.return_value = True
    mock_item1.is_file.return_value = False

    mock_item2 = MagicMock(spec=Path)
    mock_item2.is_dir.return_value = False
    mock_item2.is_file.return_value = True

    with patch.object(Path, "exists", return_value=True), \
         patch.object(Path, "iterdir", side_effect=[
            [mock_item1, mock_item2],  # First directory with items
            []  # Second dir is empty
         ]), patch("analyticq.util.AnalyticQConst", MockAnalyticQConst):

        await codebase_cleaner.cleanup_old_codebase(dry_run=True)

        assert codebase_cleaner._is_item_old.call_count == 2
        assert codebase_cleaner._delete_item.call_count == 2
