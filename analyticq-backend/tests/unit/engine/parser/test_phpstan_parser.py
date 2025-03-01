import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.engine.parser import PHPStanParser
from analyticq.exception import ScanParserException


@pytest.fixture
def phpstan_parser():
    return PHPStanParser()


@pytest.fixture
def sample_phpstan_output():
    return {
        "totals": {
            "errors": 0,
            "file_errors": 2
        },
        "files": {
            "/code/test.php": {
                "errors": 2,
                "messages": [
                    {
                        "message": "Property App\\Tests\\User::$name is never read, only written.",
                        "line": 7,
                        "ignorable": True,
                        "tip": "See: https://phpstan.org/docs",
                        "identifier": "property.onlyWritten"
                    },
                    {
                        "message": "Method return type missing",
                        "line": 15,
                        "ignorable": False,
                        "identifier": "missingType.return"
                    }
                ]
            }
        },
        "errors": []
    }


@pytest.fixture
def empty_phpstan_output():
    return {
        "totals": {"errors": 0, "file_errors": 0},
        "files": {},
        "errors": []
    }


def test_parser_initialization():
    """Test parser initialization and field mapping"""
    parser = PHPStanParser()
    assert parser.tool_name == "PHPStan"
    assert parser.field_mapping == {
        "rule_id": "title",
        "message": "description",
        "path": "file_path",
        "start_line": "line_number",
        'end_line': 'line_number',
        'metadata': 'metadata'
    }


def test_confidence_mapping(phpstan_parser):
    severity_low = phpstan_parser._map_confidence(True)
    assert severity_low == AnalyticQConfidence.LOW

    severity_unknown = phpstan_parser._map_confidence(False)
    assert severity_unknown == AnalyticQConfidence.UNKNOWN


def test_severity_mapping(phpstan_parser):
    severity = phpstan_parser._map_severity("any_level")
    assert severity == AnalyticQSeverity.UNKNOWN


def test_successfull_parse(phpstan_parser, sample_phpstan_output):
    result = phpstan_parser.parse_scan_result(sample_phpstan_output)

    assert isinstance(result, AnalyticQSASTScanResult)

    # Check metadata
    assert result.metadata["metrics"] == sample_phpstan_output["totals"]
    assert result.metadata["total_files_analyzed"] == 1
    assert result.metadata["tool_specific"]["errors"] == []

    # Check issues
    assert len(result.issues) == 2

    first_issue = result.issues[0]
    assert first_issue.rule_id == "property.onlyWritten"
    assert first_issue.message == "Property App\\Tests\\User::$name is never read, only written."
    assert first_issue.path == "/code/test.php"
    assert first_issue.start_line == 7
    assert first_issue.metadata["tip"] == "See: https://phpstan.org/docs"
    assert first_issue.metadata["identifier"] == "property.onlyWritten"


def test_null_input(phpstan_parser):
    """Test handling of null input"""
    with pytest.raises(ScanParserException) as exc_info:
        phpstan_parser.parse_scan_result(None)
    assert "Unexpected error parsing PHPStan results" in str(exc_info.value)


def test_empty_output_parse(phpstan_parser, empty_phpstan_output):
    result = phpstan_parser.parse_scan_result(empty_phpstan_output)

    assert isinstance(result, AnalyticQSASTScanResult)
    assert result.metadata["tool_name"] == "PHPStan"
    assert len(result.issues) == 0
    assert result.metadata["total_files_analyzed"] == 0


def test_missing_files_section(phpstan_parser):
    invalid_output = {"totals": {}, "errors": []}
    result = phpstan_parser.parse_scan_result(invalid_output)

    assert isinstance(result, AnalyticQSASTScanResult)
    assert len(result.issues) == 0
    assert result.metadata["total_files_analyzed"] == 0


def test_metadata_preservation(phpstan_parser, sample_phpstan_output):
    result = phpstan_parser.parse_scan_result(sample_phpstan_output)

    assert "metrics" in result.metadata
    assert "total_files_analyzed" in result.metadata
    assert "tool_specific" in result.metadata

    assert result.metadata["metrics"] == sample_phpstan_output["totals"]
    assert result.metadata["total_files_analyzed"] == 1

    first_issue = result.issues[0]
    print(first_issue)
    assert "tip" in first_issue.metadata
    assert "identifier" in first_issue.metadata


def test_multiple_files(phpstan_parser):
    multi_file_output = {
        "totals": {"errors": 0, "file_errors": 3},
        "files": {
            "/code/file1.php": {
                "errors": 2,
                "messages": [
                    {
                        "message": "Error 1",
                        "line": 1,
                        "identifier": "error.1"
                    }
                ]
            },
            "/code/file2.php": {
                "errors": 1,
                "messages": [
                    {
                        "message": "Error 2",
                        "line": 2,
                        "identifier": "error.2"
                    }
                ]
            }
        },
        "errors": []
    }

    result = phpstan_parser.parse_scan_result(multi_file_output)
    assert len(result.issues) == 2
    assert result.metadata["total_files_analyzed"] == 2

    file_paths = set(issue.path for issue in result.issues)
    assert file_paths == {"/code/file1.php", "/code/file2.php"}
