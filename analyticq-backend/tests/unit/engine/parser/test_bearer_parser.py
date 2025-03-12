from unittest.mock import patch

import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
# Import the BearerParser class
# Assuming the class is in a module named bearer_parser.py
from analyticq.engine.parser import BearerParser
from analyticq.exception import ScanParserException


@pytest.fixture
def bearer_parser():
    return BearerParser()


# Sample data fixture
@pytest.fixture
def sample_raw_result():
    return {
        "critical": [
            {
                "id": "python_aws_hardcoded_secret",
                "title": "AWS credentials hardcoded",
                "full_filename": "/app/src/config.py",
                "line_number": 42,
                "code_extract": "aws_key = 'AKIAIOSFODNN7EXAMPLE'",
                "description": "AWS credentials should not be hardcoded",
                "cwe_ids": ["CWE-798"],
                "fingerprint": "abc123fingerprint",
                "source": {
                    "column": {
                        "start": 10,
                        "end": 30
                    }
                }
            }
        ],
        "high": [
            {
                "id": "python_sql_injection",
                "title": "Potential SQL Injection",
                "full_filename": "/app/src/database.py",
                "line_number": 23,
                "code_extract": "cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")",
                "description": "User input should be parameterized",
                "cwe_ids": ["CWE-89"],
                "fingerprint": "def456fingerprint",
                "source": {
                    "column": {
                        "start": 15,
                        "end": 50
                    }
                }
            }
        ],
        "medium": [],
        "low": [],
        "info": []
    }


def test_init(bearer_parser):
    """Test initialization of the BearerParser."""
    assert bearer_parser.tool_name == "bearer"
    assert bearer_parser.field_mapping == {
        "rule_id": "id",
        "message": "title",
        "code": "code_extract",
        "path": "full_filename",
        "start_line": "line_number",
        "endl_line": "line_number",
        "column": "column_info.start",
        "severity": "severity_level",
        "issue_metadata": "metadata"
    }


def test_map_confidence(bearer_parser):
    confidence = bearer_parser._map_confidence("any_value")
    assert confidence == AnalyticQConfidence.UNKNOWN


def test_map_severity_valid(bearer_parser):
    """Test mapping valid severity levels."""
    severities = {
        "critical": AnalyticQSeverity.CRITICAL,
        "high": AnalyticQSeverity.HIGH,
        "medium": AnalyticQSeverity.MEDIUM,
        "low": AnalyticQSeverity.LOW,
        "info": AnalyticQSeverity.INFO
    }

    for input_severity, expected_severity in severities.items():
        assert bearer_parser._map_severity(input_severity) == expected_severity


def test_map_severity_unknown(bearer_parser):
    assert bearer_parser._map_severity(None) == AnalyticQSeverity.UNKNOWN
    assert bearer_parser._map_severity("") == AnalyticQSeverity.UNKNOWN


def test_map_severity_invalid(bearer_parser):
    """Test that invalid severity levels raise exceptions."""
    with pytest.raises(ValueError):
        bearer_parser._map_severity("not_a_valid_severity")


def test_transform_output(bearer_parser, sample_raw_result):

    transformed_issues = bearer_parser.transform_output(sample_raw_result)

    # Check we have the correct number of issues
    assert len(transformed_issues) == 2

    critical_issue = transformed_issues[0]

    assert critical_issue["id"] == "python_aws_hardcoded_secret"
    assert critical_issue["title"] == "AWS credentials hardcoded"
    assert critical_issue["severity_level"] == "critical"
    assert critical_issue["full_filename"] == "/app/src/config.py"
    assert critical_issue["line_number"] == 42
    assert critical_issue["code_extract"] == "aws_key = 'AKIAIOSFODNN7EXAMPLE'"
    assert critical_issue["column"]["start"] == 10
    assert critical_issue["column"]["end"] == 30
    assert critical_issue["metadata"]["description"] == "AWS credentials should not be hardcoded"
    assert critical_issue["metadata"]["cwe_ids"] == ["CWE-798"]
    assert critical_issue["metadata"]["fingerprint"] == "abc123fingerprint"

    high_issue = transformed_issues[1]
    assert high_issue["id"] == "python_sql_injection"
    assert high_issue["severity_level"] == "high"


def test_transform_output_empty_result(bearer_parser):
    """Test transformation with an empty result."""
    empty_result = {}
    transformed_issues = bearer_parser.transform_output(empty_result)
    assert transformed_issues == []


def test_transform_output_malformed_result(bearer_parser):
    """Test transformation with malformed data."""
    malformed_result = {
        "critical": "not_a_list",  # Should be a list but is a string
        "high": [{"incomplete": "issue"}]  # Missing required fields
    }
    transformed_issues = bearer_parser.transform_output(malformed_result)

    assert len(transformed_issues) == 1

    assert transformed_issues[0]["id"] == "unknown"
    assert transformed_issues[0]["title"] == "unknown"


def test_edge_case_missing_source(bearer_parser):
    """Test handling of issues with missing source information."""
    raw_result = {
        "critical": [
            {
                "id": "missing_source",
                "title": "Issue with missing source",
                "full_filename": "/app/src/file.py",
                "line_number": 100,
                "code_extract": "print('Vulnerable code')",
                # No source field
            }
        ]
    }

    transformed = bearer_parser.transform_output(raw_result)

    # Check that the column info defaults are set correctly
    assert transformed[0]["column"] == {}


@patch('analyticq.engine.core.AnalyticQResultParser.parse_scan_result')
def test_scan_parse_result(mock_super_parse, bearer_parser, sample_raw_result):
    mock_result = AnalyticQSASTScanResultModel(
        scan_id="1",
        summary={},
        scan_metadata={},
        issues=[]
    )
    mock_super_parse.return_value = mock_result

    result = bearer_parser.parse_scan_result(sample_raw_result)

    mock_super_parse.assert_called_once()

    # Check that scan metadata was updated correctly
    assert result.scan_metadata["total_critical"] == 1
    assert result.scan_metadata["total_high"] == 1
    assert result.scan_metadata["total_medium"] == 0
    assert result.scan_metadata["total_low"] == 0
    assert result.scan_metadata["total_info"] == 0


def test_parse_scan_result_exception(bearer_parser):

    with patch.object(bearer_parser, "transform_output", side_effect=Exception("Test exception")):
        with pytest.raises(ScanParserException) as excinfo:
            bearer_parser.parse_scan_result({"critical": []})

        assert "Unexpected error parsing Bearer results" in str(excinfo.value)
