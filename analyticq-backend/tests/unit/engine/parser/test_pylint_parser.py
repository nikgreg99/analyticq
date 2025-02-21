import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.engine.parser import PylintParser
from analyticq.exception import ScanParserException


@pytest.fixture
def parser():
    return PylintParser()


@pytest.fixture
def sample_pylint_result():
    return [
        {
            "type": "warning",
            "module": "example",
            "obj": "example_function",
            "line": 42,
            "endLine": 43,
            "column": 0,
            "path": "src/example.py",
            "symbol": "unused-variable",
            "message": "Unused variable 'x'",
            "message-id": "W0612"
        },
        {
            "type": "error",
            "module": "example",
            "obj": "another_function",
            "line": 50,
            "column": 0,
            "path": "src/example.py",
            "symbol": "undefined-variable",
            "message": "Undefined variable 'y'",
            "message-id": "E0602"
        }
    ]


def test_successful_parse(parser, sample_pylint_result):
    result = parser.parse_scan_result(sample_pylint_result)

    assert isinstance(result, AnalyticQSASTScanResult)
    assert isinstance(result.issues, list)
    assert len(result.issues) == 2

    # Check first issue
    issue1 = result.issues[0]
    assert isinstance(issue1, AnalyticQSASTIssue)
    assert issue1.code == "example_function"
    assert issue1.rule_id == "W0612"
    assert issue1.severity == AnalyticQSeverity.MEDIUM
    assert issue1.message == "Unused variable 'x'"
    assert issue1.path == "src/example.py"
    assert issue1.start_line == 42
    assert issue1.end_line == 43
    assert issue1.confidence == AnalyticQConfidence.UNKNOWN

    # Check summary
    assert result.summary["total"] == 2
    assert result.summary["by_severity"]["MEDIUM"] == 1
    assert result.summary["by_severity"]["HIGH"] == 1

    # Check metadata
    assert result.metadata["tool_name"] == "Pylint"
    assert result.metadata["metrics"] == {}


def test_parse_missing_endline(parser):
    result = [{
        "type": "warning",
        "module": "example",
        "obj": "example_function",
        "line": 42,
        "column": 0,
        "path": "src/example.py",
        "symbol": "unused-variable",
        "message": "Unused variable 'x'",
        "message-id": "W0612"
    }]

    parsed = parser.parse_scan_result(result)
    assert parsed.issues[0].end_line != parsed.issues[0].start_line


def test_parse_empty_result(parser):
    result = parser.parse_scan_result([])
    assert isinstance(result, AnalyticQSASTScanResult)
    assert len(result.issues) == 0
    assert result.summary["total"] == 0
    assert all(result.summary["by_severity"][sev.value] == 0 for sev in AnalyticQSeverity)


def test_invalid_input_type(parser):
    with pytest.raises(ScanParserException):
        parser.parse_scan_result("not a dict")
