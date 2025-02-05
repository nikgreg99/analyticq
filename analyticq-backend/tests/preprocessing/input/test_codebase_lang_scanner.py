import logging
from collections import defaultdict
from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest
from analyticq.config import AnalyticQBaseConfig
from analyticq.preprocessing import (CodebaseLangScanner,
                                     CodebaseMetricsReporter)
from analyticq.util import PathUtil, TimeTrackerUtils

logger = logging.getLogger(__name__)


@pytest.fixture
def mock_batch_util():
    # Create the BatchParameters instance with reasonable defaults
    @dataclass
    class MockBatchParameters:
        batch_size: int = 100
        max_concurrency: int = 1
        load_factor: float = 1.0

    # Create the mock
    batch_util = Mock()

    async def mock_adjust_parameters():
        return MockBatchParameters()

    batch_util.adjust_parameters.side_effect = mock_adjust_parameters

    # Mock get_batch_ranges to return a single batch
    batch_util.get_batch_ranges.return_value = [(0, 100)]

    # Mock current_parameters property
    batch_util.current_parameters = MockBatchParameters()

    return batch_util


@pytest.fixture(autouse=True)
def mock_metrics_reporter():
    reporter_metric = Mock(spec=CodebaseMetricsReporter)
    reporter_metric.add_file_statistics = Mock()
    reporter_metric.add_excluded_file = Mock()
    reporter_metric.add_excluded_dir = Mock()
    reporter_metric.get_collected_data = Mock(return_value={})
    reporter_metric.reset_mock()
    return reporter_metric


@pytest.fixture
def mock_time_tracker():
    tracker = Mock(spec=TimeTrackerUtils)
    tracker.start = Mock()
    tracker.update = Mock()
    tracker.stop = Mock()
    return tracker


@pytest.fixture
def scanner(mock_metrics_reporter, mock_time_tracker, mock_batch_util):
    return CodebaseLangScanner(
        metrics_reporter=mock_metrics_reporter,
        time_tracker=mock_time_tracker,
        batch_util=mock_batch_util
    )


@pytest.mark.asyncio
async def test_detect_language_and_loc_python_file(scanner, tmp_path):
    # Create a temporary Python file
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass\n")

    language, loc = await scanner.detect_language_and_loc(test_file)

    assert language == "Python", "Language should be Python"
    assert loc == 2, "LOC should be 2"


@pytest.mark.asyncio
async def test_detect_language_and_loc_text_only(scanner, tmp_path):
    test_file = tmp_path / "empty.txt"
    test_file.write_bytes(b"")

    language, loc = await scanner.detect_language_and_loc(test_file)

    assert language == "Text only", "Language should be Text only"
    assert loc == 0, "LOC should be 0"


@pytest.mark.asyncio
async def test_process_file_relevant(scanner, tmp_path):
    conf_path = PathUtil.get_backend_default_test_file_AnalyticQ_path()
    conf_path = conf_path / "test_config.json"
    AnalyticQBaseConfig.from_file(conf_path)

    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")

    file_group = defaultdict(list)
    await scanner.process_file(test_file, file_group)

    scanner.metrics_reporter.add_file_statistics.assert_called_once()
    assert "Python" in file_group, "Python should be in file group"


@pytest.mark.asyncio
async def test_process_file_excluded(scanner, tmp_path):
    conf_path = PathUtil.get_backend_default_test_file_AnalyticQ_path()
    conf_path = conf_path / "test_config.json"
    AnalyticQBaseConfig.from_file(conf_path)

    sample_file = tmp_path / "sample.exe"
    sample_file.write_text("")

    file_group = defaultdict(list)
    await scanner.process_file(sample_file, file_group)

    scanner.metrics_reporter.add_excluded_file.assert_called_once()
    assert len(file_group) == 0, f"Expceted 0, got {len(file_group)}"


@pytest.mark.asyncio
async def test_process_dir(scanner, tmp_path):
    conf_path = PathUtil.get_backend_default_test_file_AnalyticQ_path()
    conf_path = conf_path / "test_config.json"
    AnalyticQBaseConfig.from_file(conf_path)

    src_dir = tmp_path / "src"
    src_dir.mkdir()

    py_file = src_dir / "main.py"
    py_file.write_text("print('hello')")

    js_file = src_dir / "script.js"
    js_file.write_text("console.log('hello')")

    file_group = defaultdict(list)
    with patch("analyticq.preprocessing.DirFilter.is_irrelevant_dir", return_value=False):
        await scanner.process_dir(src_dir, file_group)

    assert len(file_group) > 0, "Exptected dict not empty"
    scanner.time_tracker.update.assert_called()


@pytest.mark.asyncio
async def test_error_handling(scanner, tmp_path):
    non_existent = tmp_path / "not_exists.py"
    file_group = defaultdict(list)

    await scanner.process_file(non_existent, file_group)

    assert len(file_group) == 0, "Expected no files ared added"


@pytest.mark.asyncio
async def test_scan_codebase_languages(scanner, tmp_path):
    conf_path = PathUtil.get_backend_default_test_file_AnalyticQ_path()
    conf_path = conf_path / "test_config.json"
    AnalyticQBaseConfig.from_file(conf_path)

    # Create a temporary directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    py_file = src_dir / "main.py"

    py_file.write_text("print('hello')")

    js_file = src_dir / "script.js"
    js_file.write_text("console.log('hello')")

    with patch("analyticq.preprocessing.DirFilter.is_irrelevant_dir", return_value=False):
        await scanner.scan_codebase(src_dir)

    scanner.time_tracker.start.assert_called_once()
    scanner.time_tracker.stop.assert_called_once()
    scanner.metrics_reporter.add_file_statistics.assert_any_call(py_file, "Python", py_file.stat().st_size, 1)
    scanner.metrics_reporter.add_file_statistics.assert_any_call(js_file, "JavaScript", js_file.stat().st_size, 1)


@pytest.mark.asyncio
async def test_get_language_metric_report(scanner, tmp_path):
    conf_path = PathUtil.get_backend_default_test_file_AnalyticQ_path()
    conf_path = conf_path / "test_config.json"
    AnalyticQBaseConfig.from_file(conf_path)

    # Create a temporary directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    py_file = src_dir / "main.py"

    py_file.write_text("print('hello')")

    js_file = src_dir / "script.js"
    js_file.write_text("console.log('hello')")

    with patch("analyticq.preprocessing.DirFilter.is_irrelevant_dir", return_value=False):
        await scanner.scan_codebase(src_dir)

    language_report = scanner.generate_codebase_report()

    assert language_report is not {}, "Expected report not to be empty"
