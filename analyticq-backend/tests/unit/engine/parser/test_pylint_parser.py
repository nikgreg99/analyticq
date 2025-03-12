import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.engine.parser import PylintParser
from analyticq.exception import ScanParserException


@pytest.fixture
def pylint_parser() -> PylintParser:
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


def test_init_pylint_parser(pylint_parser):
    assert pylint_parser.tool_name == "Pylint"
    assert pylint_parser.field_mapping == {
        "code": "obj",
        "rule_id": "message-id",
        "start_line": "line",
        "message": "message",
        "path": "path",
        "end_line": "endLine",
        "severity": "type"
    }


def test_successful_parse(pylint_parser, sample_pylint_result):
    result = pylint_parser.parse_scan_result(sample_pylint_result)

    assert isinstance(result, AnalyticQSASTScanResultModel)
    assert isinstance(result.issues, list)
    assert len(result.issues) == 2

    # Check first issue
    issue1 = result.issues[0]
    assert isinstance(issue1, AnalyticQSASTIssueModel)
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
    assert result.scan_metadata["tool_name"] == "Pylint"
    assert result.scan_metadata["metrics"] == {}


def test_parse_missing_endline(pylint_parser):
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

    parsed = pylint_parser.parse_scan_result(result)
    assert parsed.issues[0].end_line != parsed.issues[0].start_line


def test_severity_mapping(pylint_parser):
    assert pylint_parser._map_severity("error") == AnalyticQSeverity.HIGH
    assert pylint_parser._map_severity("warning") == AnalyticQSeverity.MEDIUM
    assert pylint_parser._map_severity("refactor") == AnalyticQSeverity.LOW


def test_confidence_mapping(pylint_parser):
    assert pylint_parser._map_confidence("any") == AnalyticQConfidence.UNKNOWN


def test_parse_empty_result(pylint_parser):
    result = pylint_parser.parse_scan_result([])
    assert isinstance(result, AnalyticQSASTScanResultModel)
    assert len(result.issues) == 0
    assert result.summary["total"] == 0
    assert all(result.summary["by_severity"][sev.value] == 0 for sev in AnalyticQSeverity)


def test_invalid_input_type(pylint_parser):
    with pytest.raises(ScanParserException):
        pylint_parser.parse_scan_result("not a dict")
