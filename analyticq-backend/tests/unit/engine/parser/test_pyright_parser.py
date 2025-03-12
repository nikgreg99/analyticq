import pytest
# Import your PyrightParser class - adjust the import path as needed
from analyticq.engine import PyrightParser
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.exception import ScanParserException


@pytest.fixture
def sample_pyright_data():
    return {
        "version": "1.1.291",
        "generalDiagnostics": [
            {
                "file": "/path/to/file.py",
                "severity": "error",
                "message": "Name 'undefined_var' is not defined",
                "rule": "reportUndefinedVariable",
                "range": {
                    "start": {"line": 10, "character": 5},
                    "end": {"line": 10, "character": 18}
                }
            },
            {
                "file": "/path/to/file.py",
                "severity": "warning",
                "message": "Import could not be resolved",
                "rule": "reportMissingImports",
                "range": {
                    "start": {"line": 2, "character": 0},
                    "end": {"line": 2, "character": 15}
                }
            },
            {
                "file": "/path/to/another_file.py",
                "severity": "information",
                "message": "Type of 'var' is unknown",
                "rule": "reportUnknownVariableType",
                "range": {
                    "start": {"line": 5, "character": 4},
                    "end": {"line": 5, "character": 7}
                }
            }
        ],
        "summary": {
            "filesAnalyzed": 2,
            "errorCount": 1,
            "warningCount": 1,
            "informationCount": 1
        }
    }


@pytest.fixture
def pyright_parser() -> PyrightParser:
    return PyrightParser()


def test_severity_mapping(pyright_parser):
    """Test the severity mapping functionality."""
    assert pyright_parser._map_severity("error") == AnalyticQSeverity.HIGH
    assert pyright_parser._map_severity("warning") == AnalyticQSeverity.MEDIUM
    assert pyright_parser._map_severity("information") == AnalyticQSeverity.INFO
    assert pyright_parser._map_severity("none") == AnalyticQSeverity.UNKNOWN
    assert pyright_parser._map_severity(None) == AnalyticQSeverity.UNKNOWN
    assert pyright_parser._map_severity("invalid_severity") == AnalyticQSeverity.UNKNOWN


def test_confidence_mapping(pyright_parser):
    """Test the confidence mapping functionality."""
    assert pyright_parser._map_confidence("any_value") == AnalyticQConfidence.UNKNOWN


def test_parse_scan_result(pyright_parser, sample_pyright_data):
    """Test the parsing of a sample pyright result."""
    scan_result = pyright_parser.parse_scan_result(sample_pyright_data)

    # Verify issues count
    assert len(scan_result.issues) == 3

    # Verify first issue
    first_issue = scan_result.issues[0]
    assert first_issue.rule_id == "reportUndefinedVariable"
    assert first_issue.message == "Name 'undefined_var' is not defined"
    assert first_issue.path == "/path/to/file.py"
    assert first_issue.start_line == 10
    assert first_issue.end_line == 10
    assert first_issue.severity == AnalyticQSeverity.HIGH

    # Verify metadata
    assert scan_result.scan_metadata["version"] == "1.1.291"
    assert scan_result.scan_metadata["metrics"]["filesAnalyzed"] == 2
    assert scan_result.scan_metadata["metrics"]["errorCount"] == 1
    assert scan_result.scan_metadata["metrics"]["warningCount"] == 1
    assert scan_result.scan_metadata["metrics"]["informationCount"] == 1


def test_invalid_input(pyright_parser):
    """Test parsing with invalid input."""
    with pytest.raises(ScanParserException):
        pyright_parser.parse_scan_result({})  # Empty dict

    with pytest.raises(ScanParserException):
        pyright_parser.parse_scan_result({"generalDiagnostics": "not_a_list"})

    with pytest.raises(ScanParserException):
        pyright_parser.parse_scan_result(None)


def test_empty_diagnostics(pyright_parser):
    """Test parsing with empty diagnostics list."""
    empty_diagnostics_data = {
        "version": "1.1.291",
        "generalDiagnostics": [],
        "summary": {
            "filesAnalyzed": 10,
            "errorCount": 0,
            "warningCount": 0,
            "informationCount": 0
        }
    }
    result = pyright_parser.parse_scan_result(empty_diagnostics_data)
    assert len(result.issues) == 0
    assert result.scan_metadata["metrics"]["filesAnalyzed"] == 10


def test_partial_summary(pyright_parser, sample_pyright_data):
    """Test parsing with partial summary information."""
    # Create a copy with incomplete summary
    data_with_partial_summary = sample_pyright_data.copy()
    data_with_partial_summary["summary"] = {
        "filesAnalyzed": 2
        # Missing error, warning, and information counts
    }

    result = pyright_parser.parse_scan_result(data_with_partial_summary)
    assert result.scan_metadata["metrics"]["filesAnalyzed"] == 2
    assert result.scan_metadata["metrics"]["errorCount"] == 0  # Default value
