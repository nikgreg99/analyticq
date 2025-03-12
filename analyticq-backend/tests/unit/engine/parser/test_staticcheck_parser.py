from datetime import UTC, datetime

import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.engine.parser import StaticCheckParser
from analyticq.exception import ScanParserException


@pytest.fixture
def staticcheck_parser():
    return StaticCheckParser()


@pytest.fixture
def valid_raw_result():
    return [{
        "severity": "error",
        "code": "TEST001",
        "message": "Test error message",
        "location": {
            "file": "/path/to/file.py",
            "line": 10
        },
        "end": {
            "file": "/path/to/file.py",
            "line": 15
        }
    }]


def test_successful_parsing(staticcheck_parser, valid_raw_result, monkeypatch):
    mock_date_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("datetime.datetime", mock_date_now)
    result = staticcheck_parser.parse_scan_result(valid_raw_result)

    assert isinstance(result, AnalyticQSASTScanResultModel)
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.rule_id == "TEST001"
    assert issue.severity == AnalyticQSeverity.HIGH
    assert issue.message == "Test error message"
    assert issue.path == "/path/to/file.py"
    assert issue.start_line == 10
    assert issue.end_line == 15
    assert issue.confidence == AnalyticQConfidence.UNKNOWN


def test_multiple_issues(staticcheck_parser):

    raw_result = [
        {
            "severity": "error",
            "code": "TEST001",
            "message": "Error message",
            "location": {"file": "/path/to/file1.py", "line": 10},
            "end": {"line": 15}
        },
        {
            "severity": "warning",
            "code": "TEST002",
            "message": "Warning message",
            "location": {"file": "/path/to/file2.py", "line": 20},
            "end": {"line": 25}
        }
    ]

    result = staticcheck_parser.parse_scan_result(raw_result)

    assert len(result.issues) == 2
    assert result.summary["total"] == 2
    assert result.summary["by_severity"]["HIGH"] == 1
    assert result.summary["by_severity"]["MEDIUM"] == 1


def test_severity_mapping(staticcheck_parser):
    assert staticcheck_parser._map_severity("error") == AnalyticQSeverity.HIGH
    assert staticcheck_parser._map_severity("warning") == AnalyticQSeverity.MEDIUM
    assert staticcheck_parser._map_severity("info") == AnalyticQSeverity.LOW
    assert staticcheck_parser._map_severity("unknown") == AnalyticQSeverity.UNKNOWN


def test_confidence_mapping(staticcheck_parser):
    assert staticcheck_parser._map_confidence("any") == AnalyticQConfidence.UNKNOWN


def test_invalid_severity(staticcheck_parser):
    raw_result = [{
        "severity": "INVALID",
        "code": "TEST001",
        "message": "Test message",
        "location": {"file": "file.py", "line": 1},
        "end": {"line": 2}
    }]

    with pytest.raises(ScanParserException):
        staticcheck_parser.parse_scan_result(raw_result)


def test_empty_result(staticcheck_parser):
    result = staticcheck_parser.parse_scan_result([])

    assert isinstance(result, AnalyticQSASTScanResultModel)
    assert len(result.issues) == 0
    assert result.summary["total"] == 0
    assert all(result.summary["by_severity"][sev.value] == 0 for sev in AnalyticQSeverity)


def test_metadata(staticcheck_parser):
    result = staticcheck_parser.parse_scan_result([])

    assert result.scan_metadata["tool_name"] == "Staticcheck"
    assert isinstance(result.scan_metadata["metrics"], dict)
    assert len(result.scan_metadata["metrics"]) == 0
