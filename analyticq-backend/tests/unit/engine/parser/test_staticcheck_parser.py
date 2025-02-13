import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.engine.parser import StaticCheckParser
from analyticq.exception import ScanParserException


@pytest.fixture
def parser():
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
            "line": 15
        }
    }]


def test_successful_parsing(parser, valid_raw_result):
    result = parser.parse_scan_result(valid_raw_result)

    assert isinstance(result, AnalyticQSASTScanResult)
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.issue_id == "TEST001"
    assert issue.code == "TEST001"
    assert issue.rule_id == "TEST001"
    assert issue.severity == AnalyticQSeverity.HIGH
    assert issue.message == "Test error message"
    assert issue.path == "/path/to/file.py"
    assert issue.start_line == 10
    assert issue.end_line == 15
    assert issue.confidence == AnalyticQConfidence.UNKNOWN


def test_multiple_issues(parser):
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

    result = parser.parse_scan_result(raw_result)

    assert len(result.issues) == 2
    assert result.summary["total"] == 2
    assert result.summary["by_severity"]["HIGH"] == 1
    assert result.summary["by_severity"]["MEDIUM"] == 1


def test_severity_mapping(parser):
    raw_result = [
        {
            "severity": "error",
            "code": "TEST001",
            "message": "Message",
            "location": {"file": "file.py", "line": 1},
            "end": {"line": 2}
        },
        {
            "severity": "warning",
            "code": "TEST002",
            "message": "Message",
            "location": {"file": "file.py", "line": 3},
            "end": {"line": 4}
        },
        {
            "severity": "info",
            "code": "TEST003",
            "message": "Message",
            "location": {"file": "file.py", "line": 5},
            "end": {"line": 6}
        }
    ]

    result = parser.parse_scan_result(raw_result)
    severities = [issue.severity for issue in result.issues]
    assert severities == [
        AnalyticQSeverity.HIGH,
        AnalyticQSeverity.MEDIUM,
        AnalyticQSeverity.LOW
    ]


def test_missing_required_fields(parser):
    invalid_result = [{
        "severity": "error",
        # Missing location field
        "code": "TEST001",
        "message": "Test message"
    }]

    with pytest.raises(ScanParserException) as exc_info:
        parser.parse_scan_result(invalid_result)
    assert "Failed to parse StaticCheck results" in str(exc_info.value)


def test_invalid_severity(parser):
    raw_result = [{
        "severity": "INVALID",
        "code": "TEST001",
        "message": "Test message",
        "location": {"file": "file.py", "line": 1},
        "end": {"line": 2}
    }]

    result = parser.parse_scan_result(raw_result)
    assert result.issues[0].severity == AnalyticQSeverity.UNKNOWN


def test_empty_result(parser):
    result = parser.parse_scan_result([])

    assert isinstance(result, AnalyticQSASTScanResult)
    assert len(result.issues) == 0
    assert result.summary["total"] == 0
    assert all(result.summary["by_severity"][sev.value] == 0 for sev in AnalyticQSeverity)


def test_metadata(parser):
    result = parser.parse_scan_result([])

    assert result.metadata["tool"] == "StaticCheck"
    assert isinstance(result.metadata["metrics"], dict)
    assert len(result.metadata["metrics"]) == 0
