import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.engine.parser import FlakeParser
from analyticq.exception import ScanParserException


@pytest.fixture
def flake_parser() -> FlakeParser:
    return FlakeParser()


@pytest.fixture
def sample_flake8_output():
    """Sample Flake8 output for testing."""
    return {
        '/path/to/file1.py': [
            {
                'code': 'E999',
                'filename': '/path/to/file1.py',
                'line_number': 11,
                'column_number': 35,
                'text': 'IndentationError: unindent does not match any outer indentation level',
                'physical_line': None
            },
            {
                'code': 'F401',
                'filename': '/path/to/file1.py',
                'line_number': 2,
                'column_number': 1,
                'text': "'module' imported but unused",
                'physical_line': 'import module'
            }
        ],
        '/path/to/file2.py': [
            {
                'code': 'W291',
                'filename': '/path/to/file2.py',
                'line_number': 5,
                'column_number': 80,
                'text': 'trailing whitespace',
                'physical_line': 'def function():    '
            },
            {
                'code': 'C901',
                'filename': '/path/to/file2.py',
                'line_number': 10,
                'column_number': 0,
                'text': 'function is too complex (15)',
                'physical_line': 'def complex_function():'
            }
        ]
    }


def test_parser_initialization(flake_parser):
    """Test that the parser initializes with the correct tool name and field mapping."""
    assert flake_parser.tool_name == "flake8"
    assert "rule_id" in flake_parser.field_mapping
    assert flake_parser.field_mapping["rule_id"] == "code"
    assert flake_parser.field_mapping["path"] == "filename"


def test_map_severity(flake_parser):
    """Test that severity mapping works correctly for different Flake8 error codes."""
    assert flake_parser._map_severity("E999") == AnalyticQSeverity.HIGH
    assert flake_parser._map_severity("F401") == AnalyticQSeverity.CRITICAL
    assert flake_parser._map_severity("W291") == AnalyticQSeverity.MEDIUM
    assert flake_parser._map_severity("C901") == AnalyticQSeverity.LOW
    assert flake_parser._map_severity("N801") == AnalyticQSeverity.LOW

    # Test edge cases
    assert flake_parser._map_severity(None) == AnalyticQSeverity.UNKNOWN
    assert flake_parser._map_severity("") == AnalyticQSeverity.UNKNOWN
    assert flake_parser._map_severity(123) == AnalyticQSeverity.UNKNOWN


def test_map_confidence(flake_parser):
    """Test that confidence mapping returns the default HIGH confidence."""
    assert flake_parser._map_confidence("anything") == AnalyticQConfidence.UNKNOWN
    assert flake_parser._map_confidence(None) == AnalyticQConfidence.UNKNOWN


def test_invalid_input(flake_parser):
    """Test that the parser handles invalid input appropriately."""
    with pytest.raises(ScanParserException):
        flake_parser.parse_scan_result(None)

    with pytest.raises(ScanParserException):
        flake_parser.parse_scan_result("not a dictionary")


def test_parse_scan_result(flake_parser, sample_flake8_output):
    """Test parsing a complete Flake8 scan result."""
    # Parse the sample output
    result = flake_parser.parse_scan_result(sample_flake8_output)

    # Verify the result is a valid AnalyticQSASTScanResult
    assert isinstance(result, AnalyticQSASTScanResultModel)

    # Verify all issues were parsed
    assert len(result.issues) == 4

    # Check that issues have the correct severity based on error code
    issue_by_code = {issue.rule_id: issue for issue in result.issues}
    assert issue_by_code["E999"].severity == AnalyticQSeverity.HIGH
    assert issue_by_code["F401"].severity == AnalyticQSeverity.CRITICAL
    assert issue_by_code["W291"].severity == AnalyticQSeverity.MEDIUM
    assert issue_by_code["C901"].severity == AnalyticQSeverity.LOW

    # Check that all issues have the correct confidence
    for issue in result.issues:
        assert isinstance(issue, AnalyticQSASTIssueModel)
        assert issue.confidence == AnalyticQConfidence.UNKNOWN

    # Verify summary calculations
    assert result.summary["total"] == 4
    assert result.summary["by_severity"][AnalyticQSeverity.HIGH.value] == 1
    assert result.summary["by_severity"][AnalyticQSeverity.CRITICAL.value] == 1
    assert result.summary["by_severity"][AnalyticQSeverity.MEDIUM.value] == 1
    assert result.summary["by_severity"][AnalyticQSeverity.LOW.value] == 1

    # Verify metadata
    assert result.scan_metadata["tool_name"] == "flake8"
    assert result.scan_metadata["metrics"]["files_analyzed"] == 2
    assert result.scan_metadata["metrics"]["total_issues"] == 4


def test_file_aggregation(flake_parser):
    """Test that issues from multiple files are correctly aggregated."""
    result = flake_parser.parse_scan_result({
        'file1.py': [{'code': 'E101', 'line_number': 5, 'text': 'Error 1'}],
        'file2.py': [{'code': 'W292', 'line_number': 10, 'text': 'Warning 1'}],
        'file3.py': []  # Empty file results
    })

    assert len(result.issues) == 2, "Exptected 2 issues"
    assert result.scan_metadata["metrics"]["files_analyzed"] == 3, "Expected three file analyzed"
    assert result.scan_metadata["metrics"]["total_issues"] == 2

    # Check that filenames were correctly assigned
    paths = {issue.path for issue in result.issues}
    assert paths == {'file1.py', 'file2.py'}
