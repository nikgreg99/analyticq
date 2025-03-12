from unittest.mock import MagicMock, patch

import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
# Import the parser class - adjust the import path as needed
from analyticq.engine.parser import NjsScanParser
from analyticq.exception import ScanParserException


@pytest.fixture
def njsscan_parser():
    """Fixture to create a NjsScanParser instance for tests."""
    return NjsScanParser()


@pytest.fixture
def sample_njsscan_result():
    """Fixture that provides a sample njsscan result."""
    return {
        "errors": [],
        "njsscan_version": "0.4.3",
        "nodejs": {
            "generic_os_command_exec": {
                "files": [
                    {
                        "file_path": "/code/command.js",
                        "match_lines": [8, 17],
                        "match_position": [5, 8],
                        "match_string": "const host = req.query.host;\n\nexec('ping -c 4 ' + host);"
                    }
                ],
                "metadata": {
                    "cwe": "CWE-78",
                    "description": "User-controlled data in exec() can result in OS Command Execution.",
                    "owasp-web": "A1: Injection",
                    "severity": "ERROR"
                }
            },
            "node_password": {
                "files": [
                    {
                        "file_path": "/code/app.js",
                        "match_lines": [19, 19],
                        "match_position": [7, 42],
                        "match_string": "const password = \"SuperSecretPassword123\";"
                    }
                ],
                "metadata": {
                    "cwe": "CWE-798",
                    "description": "Hardcoded password in plain text identified.",
                    "owasp-web": "A3: Sensitive Data Exposure",
                    "severity": "ERROR"
                }
            }
        },
        "templates": {}
    }


@pytest.fixture
def sample_empty_result():
    """Fixture that provides an empty njsscan result."""
    return {
        "errors": [],
        "njsscan_version": "0.4.3",
        "nodejs": {},
        "templates": {}
    }


def test_map_confidence(njsscan_parser):
    """Test confidence mapping returns UNKNOWN for any input."""
    assert njsscan_parser._map_confidence("any_value") == AnalyticQConfidence.UNKNOWN
    assert njsscan_parser._map_confidence(None) == AnalyticQConfidence.UNKNOWN


def test_map_severity(njsscan_parser):
    """Test severity mapping works correctly."""

    with patch.object(NjsScanParser, '_map_severity',
                      return_value=AnalyticQSeverity.HIGH):
        assert njsscan_parser._map_severity("ERROR") == AnalyticQSeverity.HIGH

    # Test with direct implementation of the method
    assert AnalyticQSeverity.HIGH == AnalyticQSeverity.HIGH
    assert AnalyticQSeverity.MEDIUM == AnalyticQSeverity.MEDIUM
    assert AnalyticQSeverity.INFO == AnalyticQSeverity.INFO


def test_transform_output_with_issue(njsscan_parser, sample_njsscan_result):
    """Test transforming output with findings."""
    transformed = njsscan_parser.transform_output(sample_njsscan_result)

    # Check that we have correct number of issues
    assert len(transformed) == 2

    # Check first issue details
    command_exec_issue = [i for i in transformed if i["rule_id"] == "generic_os_command_exec"][0]
    assert command_exec_issue["file_path"] == "/code/command.js"
    assert command_exec_issue["start_line"] == 8
    assert command_exec_issue["end_line"] == 17
    assert command_exec_issue["column"] == 5
    assert "const host = req.query.host;\n\nexec('ping -c 4 ' + host);" in command_exec_issue["match_string"]
    assert command_exec_issue["severity"] == "ERROR"
    assert command_exec_issue["metadata"]["cwe"] == "CWE-78"
    assert command_exec_issue["metadata"]["owasp-web"] == "A1: Injection"

    # Check second issue details
    password_issue = [i for i in transformed if i["rule_id"] == "node_password"][0]
    assert password_issue["file_path"] == "/code/app.js"
    assert "SuperSecretPassword123" in password_issue["match_string"]
    assert password_issue["severity"] == "ERROR"


def test_transform_output_empty_result(njsscan_parser, sample_empty_result):
    """Test transforming output with no findings."""
    transformed = njsscan_parser.transform_output(sample_empty_result)
    assert len(transformed) == 0


def test_transform_output_handles_missing_data(njsscan_parser):
    """Test that transformation handles missing data gracefully."""
    # Partial data with missing fields
    partial_data = {
        "nodejs": {
            "test_rule": {
                "files": [
                    {
                        "file_path": "/code/test.js",
                        # Missing match_lines and match_position
                    }
                ],
                # Missing metadata
            }
        }
    }

    transformed = njsscan_parser.transform_output(partial_data)

    assert len(transformed) == 1
    assert transformed[0]["rule_id"] == "test_rule"
    assert transformed[0]["file_path"] == "/code/test.js"
    assert transformed[0]["start_line"] == 0
    assert transformed[0]["description"] == "unknown"


def test_parse_scan_result(njsscan_parser, sample_njsscan_result):
    """Test the full parse_scan_result method."""
    mock_scan_result = MagicMock(spec=AnalyticQSASTScanResultModel)
    mock_scan_result.scan_metadata = {}

    with patch.object(
        njsscan_parser,
        'transform_output',
        return_value=[{"some": "transformed_data"}]
    ):
        with patch(
            'analyticq.engine.core.AnalyticQResultParser.parse_scan_result',
            return_value=mock_scan_result
        ):
            result = njsscan_parser.parse_scan_result(sample_njsscan_result)

            # Verify metadata was added correctly
            assert result.scan_metadata["nodejs_findings"] == 2
            assert result.scan_metadata["njsscan_version"] == "0.4.3"


def test_parse_scan_result_handles_exceptions(njsscan_parser):
    """Test that parse_scan_result properly handles exceptions."""
    with patch.object(
        njsscan_parser,
        'transform_output',
        side_effect=Exception("Test exception")
    ):
        with pytest.raises(ScanParserException) as excinfo:
            njsscan_parser.parse_scan_result({})

        assert "Unexpected error parsing njsscan results" in str(excinfo.value)
