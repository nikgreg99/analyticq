from unittest.mock import patch

import pytest
from analyticq.util import AnalyticQConst, ResourceUtil


@pytest.fixture
def mock_psutil():
    with patch('analyticq.util.resource_util.psutil') as mock_psutil:
        yield mock_psutil


@pytest.fixture
def mock_os():
    with patch('analyticq.util.resource_util.os') as mock_os:
        yield mock_os


def test_max_workers_available_cpu_intensive_high_load(mock_psutil, mock_os):
    mock_os.cpu_count.return_value = 8
    mock_psutil.cpu_percent.return_value = 90

    result = ResourceUtil.max_workers_available(cpu_itensive=True)
    assert result == 2


def test_max_workers_available_cpu_intensive_low_load(mock_psutil, mock_os):
    mock_os.cpu_count.return_value = 8
    mock_psutil.cpu_percent.return_value = 30
    expected_max_workers = 4

    result = ResourceUtil.max_workers_available(cpu_itensive=True)
    assert result == expected_max_workers, f"Expected {expected_max_workers}, got {result}"


def test_max_workers_available_io_intensive_high_load(mock_psutil, mock_os):
    mock_os.cpu_count.return_value = 8
    mock_psutil.cpu_percent.return_value = 90
    expected_max_workers = 8

    result = ResourceUtil.max_workers_available(cpu_itensive=False)
    assert result == 8, f"Expected {expected_max_workers}, got {result}"


def test_max_workers_available_io_intensive_low_load(mock_psutil, mock_os):
    mock_os.cpu_count.return_value = 8
    mock_psutil.cpu_percent.return_value = 30
    expected_max_workers = 16

    result = ResourceUtil.max_workers_available(cpu_itensive=False)
    assert result == 16, f"Expected {expected_max_workers}, got {result}"


def test_max_batch_size_available_less_than_1000_files(mock_psutil):
    mock_psutil.virtual_memory.return_value.available = 16 * 1024 ** 3
    expected_batch_size_available = 100

    result = ResourceUtil.max_batch_size_available(total_files=500, avg_file_size_kb=100)
    assert result == 100, f"Exptected {expected_batch_size_available}, got {result}"


def test_max_batch_size_available_more_than_1000_files_sufficient_memory(mock_psutil):
    mock_psutil.virtual_memory.return_value.available = 16 * 1024 ** 3

    result = ResourceUtil.max_batch_size_available(total_files=1500, avg_file_size_kb=100)
    assert result == 5000, f"Expected {AnalyticQConst.DEFAULT_BATCH_SIZE_THRESHOLD}, got {result}"


def test_max_batch_size_available_more_than_1000_files_insufficient_memory(mock_psutil):
    mock_psutil.virtual_memory.return_value.available = 4 * 1024 ** 3
    expected_max_batch_size_available = 1000
    result = ResourceUtil.max_batch_size_available(total_files=1500, avg_file_size_kb=100)
    assert result == expected_max_batch_size_available, f"Expected {expected_max_batch_size_available}, got {result}"
