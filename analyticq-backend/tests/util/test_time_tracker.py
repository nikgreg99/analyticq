from unittest.mock import Mock, patch

import pytest
from analyticq.util import TimeTrackerUtils
from tqdm.asyncio import tqdm


@pytest.fixture
def mock_logger():
    """Fixture for mocking logger"""
    with patch('logging.getLogger') as mock_log:
        yield mock_log.return_value


@pytest.fixture
def mock_tqdm():
    with patch("analyticq.util.time_tracker.tqdm") as mock_tqdm:
        mock_progress = Mock(spec=tqdm)
        mock_progress.n = 0
        mock_progress.total = 100
        mock_tqdm.return_value = mock_progress
        yield mock_tqdm


@pytest.fixture
def time_tracker():
    return TimeTrackerUtils()


def test_init(time_tracker):
    assert time_tracker.progress_bar is None, "Progress bar should be None initially"
    assert time_tracker.start_time is None, "Start time should be None initially"
    assert time_tracker.total_files == 0, "Total files should be 0 initially"
    assert time_tracker.progress == 0.0, "Progress should be 0.0 initially"
    assert time_tracker.elapsed_time == 0.0, "Initial elapsed time should be 0"


def test_invalid_total_files(time_tracker):
    with pytest.raises(ValueError):
        time_tracker.start(0)

    with pytest.raises(ValueError):
        time_tracker.start(-1)


def test_start(time_tracker, mock_tqdm):
    with patch('time.time', return_value=1000):
        time_tracker.start(100)

    assert time_tracker.total_files == 100, "Total files should be set correctly"
    assert time_tracker.start_time == 1000, "Start time should be set correctly"
    assert time_tracker.progress_bar is not None, "Progress bar should be initialized"
    assert time_tracker.progress == 0.0, "Initial progress should be 0"

    mock_tqdm.assert_called_once_with(
        total=100,
        desc="🔍 Scanning Codebase",
        unit="file",
        dynamic_ncols=True
    )


def test_update_with_zero_elapsed_time(time_tracker, mock_tqdm):
    with patch('time.time', return_value=1000):
        time_tracker.start(100)
        time_tracker.update()

    mock_progress = time_tracker.progress_bar
    mock_progress.update.assert_called_once_with(1)
    mock_progress.set_postfix.assert_not_called()


def test_update_with_progress(time_tracker, mock_tqdm):
    with patch("time.time", side_effect=[1000, 1010]):
        time_tracker.start(100)
        mock_progress = time_tracker.progress_bar
        mock_progress.n = 50  # 50% progress
        time_tracker.update()

    assert mock_progress.update.call_count == 1, "Update should be called once"
    assert time_tracker.progress == 50.0, "Progress should reach 50%"

    postfix_calls = mock_progress.set_postfix.call_args[1]
    assert abs(float(postfix_calls["Speed"].split()[0]) - 5.0) < 0.1, "Estimated time remaining should be 5s"
    assert abs(float(postfix_calls["ETA"].split("s")[0]) - 10.0) < 0.1, "Processing speed should be 10 files/s"


def test_error_handling_during_update(time_tracker, mock_tqdm, mock_logger):
    with patch("time.time", return_value=1000):
        time_tracker.start(100)
        mock_progress = time_tracker.progress_bar
        mock_progress.n = 0

        time_tracker.update()
        mock_logger.warning.assert_not_called()


def test_stop_time_tracker(time_tracker, mock_tqdm, mock_logger):
    """Test stop method"""
    with patch('time.time', side_effect=[1000, 1030]):
        time_tracker.start(100)
        time_tracker.stop()

        assert time_tracker.progress_bar is None, "Progress bar should be cleared"


@pytest.mark.parametrize("processed,total,expected", [
    (50, 100, 50.0),
    (0, 100, 0.0),
    (100, 100, 100.0),
])
def test_progress_calculation(time_tracker, mock_tqdm, processed, total, expected):
    """Test progress calculation with various scenarios"""
    with patch('time.time', return_value=1000):
        time_tracker.start(total)
        time_tracker.progress_bar.n = processed

        assert time_tracker.progress == expected, f"Progress should be {expected}%"
