import pytest
from analyticq.engine.core import (AnalyticQConfidence, AnalyticQSASTIssue,
                                   AnalyticQSASTScanResult, AnalyticQSeverity)
from analyticq.engine.parser import BanditParser
from analyticq.exception import ScanParserException


def test_parse_empty_results(bandit_parser):
    raw_results = {
        "results": [],
        "metrics": {},
    }

    result = bandit_parser.parse_scan_result(raw_results)

    assert isinstance(result, AnalyticQSASTScanResult)
    assert len(result.issues) == 0
    assert result.summary["total"] == 0


@pytest.fixture
def bandit_parser():
    return BanditParser()


def test_parse_valid_results(bandit_parser):
    """Test parsing valid Bandit results."""
    raw_results = {
        "results": [
            {
                "code": "",
                "test_id": "B101",
                "issue_severity": "HIGH",
                "issue_text": "Hardcoded password",
                "filename": "test.py",
                "line_number": 10,
                "line_range": [
                    10, 11
                ],
                "issue_confidence": "HIGH",
            },
            {
                "code": "",
                "test_id": "B102",
                "issue_severity": "MEDIUM",
                "issue_text": "Use of insecure function",
                "filename": "test.py",
                "line_number": 20,
                "line_range": [
                    20, 21
                ],
                "issue_confidence": "MEDIUM",
            },
        ],
        "tool": "Bandit",
        "metrics": {
            "loc": 100,
            "nosec": 5,
        },
    }

    results = bandit_parser.parse_scan_result(raw_results)

    # Validate findings
    assert isinstance(results, AnalyticQSASTScanResult)
    assert len(results.issues) == 2

    issue_1 = results.issues[0]
    assert isinstance(issue_1, AnalyticQSASTIssue)
    assert issue_1.rule_id == "B101"
    assert issue_1.severity == AnalyticQSeverity.HIGH
    assert issue_1.message == "Hardcoded password"
    assert issue_1.path == "test.py"
    assert issue_1.start_line == 10
    assert issue_1.end_line == 11
    assert issue_1.confidence == AnalyticQConfidence.HIGH

    issue_2 = results.issues[1]
    assert isinstance(issue_2, AnalyticQSASTIssue)
    assert issue_2.rule_id == "B102"
    assert issue_2.severity == AnalyticQSeverity.MEDIUM
    assert issue_2.message == "Use of insecure function"
    assert issue_2.path == "test.py"
    assert issue_2.start_line == 20
    assert issue_2.end_line == 21
    assert issue_2.confidence == AnalyticQConfidence.MEDIUM

    # Validate summary
    assert results.summary["total"] == 2
    assert results.summary["by_severity"]["HIGH"] == 1
    assert results.summary["by_severity"]["MEDIUM"] == 1

    # Validate metadata
    assert results.metadata["tool"] == "Bandit"
    assert results.metadata["metrics"] == {"loc": 100, "nosec": 5}


def test_parse_missing_required_field(bandit_parser):
    """Test parsing results with missing required fields."""
    raw_results = {
        "results": [
            {
                # Missing "test_id" and "issue_severity"
                "issue_text": "Hardcoded password",
                "filename": "test.py",
                "line_number": 10,
                "issue_confidence": "HIGH",
            }
        ],
        "tool": "Bandit",
        "metrics": {},
    }

    with pytest.raises(ScanParserException, match="Failed to parse Bandit results"):
        bandit_parser.parse_scan_result(raw_results)


def test_parse_invalid_json(bandit_parser):
    """Test parsing invalid JSON data."""
    raw_results = "invalid_json"

    with pytest.raises(ScanParserException):
        bandit_parser.parse_scan_result(raw_results)
