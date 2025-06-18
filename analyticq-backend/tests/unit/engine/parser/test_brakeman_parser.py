
from datetime import UTC, datetime
from typing import Dict

import pytest
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.engine.parser import BrakemanParser
from analyticq.exception import ScanParserException


@pytest.fixture
def brakeman_parser() -> BrakemanParser:
    return BrakemanParser()


@pytest.fixture
def sample_brakeman_output() -> Dict:
    """Sample Brakeman output for testing.
    Format: https://brakemanscanner.org/docs/output_formats/
    """
    return {
        "scan_info": {
            "app_name": "TestApp",
            "rails_version": "7.0.4",
            "ruby_version": "3.1.0",
            "brakeman_version": "5.4.1",
            "start_time": "2023-01-01 12:00:00 +0000",
            "end_time": "2023-01-01 12:00:30 +0000",
            "duration": 30.5,
            "security_warnings": 3,
            "number_of_controllers": 5,
            "number_of_models": 8,
            "number_of_templates": 12,
            "checks_performed": [
                "BasicAuth",
                "CrossSiteScripting",
                "SQL",
                "Command",
                "Evaluation"
            ]
        },
        "warnings": [
            {
                "warning_code": 2,
                "warning_type": "Cross-Site Scripting",
                "message": "Unescaped model attribute",
                "file": "app/views/users/show.html.erb",
                "line": 15,
                "link": "https://brakemanscanner.org/docs/warning_types/cross_site_scripting/",
                "code": "<%= @user.name %>",
                "render_path": [
                    {
                        "type": "controller",
                        "class": "UsersController",
                        "method": "show",
                        "line": 10,
                        "file": "app/controllers/users_controller.rb"
                    }
                ],
                "location": {
                    "type": "template",
                    "template": "users/show"
                },
                "user_input": "@user.name",
                "confidence": "High",
                "cwe_id": [79]
            },
            {
                "warning_code": 0,
                "warning_type": "SQL Injection",
                "message": "Possible SQL injection",
                "file": "app/models/user.rb",
                "line": 25,
                "link": "https://brakemanscanner.org/docs/warning_types/sql_injection/",
                "code": "User.where(\"name = '#{params[:name]}'\")",
                "render_path": None,
                "location": {
                    "type": "method",
                    "class": "User",
                    "method": "find_by_name"
                },
                "user_input": "params[:name]",
                "confidence": "Medium",
                "cwe_id": [89]
            },
            {
                "warning_code": 13,
                "warning_type": "Dangerous Evaluation",
                "message": "User input in eval",
                "file": "app/controllers/admin_controller.rb",
                "line": 42,
                "link": "https://brakemanscanner.org/docs/warning_types/dangerous_evaluation/",
                "code": "eval(params[:code])",
                "render_path": None,
                "location": {
                    "type": "method",
                    "class": "AdminController",
                    "method": "execute"
                },
                "user_input": "params[:code]",
                "confidence": "High",
                "cwe_id": [95]
            }
        ],
        "ignored_warnings": [
            {
                "warning_code": 5,
                "warning_type": "Command Injection",
                "message": "Possible command injection",
                "file": "app/models/backup.rb",
                "line": 10,
                "confidence": "Low"
            }
        ],
        "errors": []
    }


@pytest.fixture
def minimal_brakeman_output() -> Dict:
    """Minimal Brakeman output with required fields only."""
    return {
        "scan_info": {
            "brakeman_version": "5.4.1"
        },
        "warnings": [
            {
                "warning_code": 1,
                "warning_type": "Test Warning",
                "message": "Test message",
                "file": "test.rb",
                "line": 1,
                "confidence": "Medium"
            }
        ]
    }


@pytest.fixture
def empty_brakeman_output() -> Dict:
    """Empty Brakeman output with no warnings."""
    return {
        "scan_info": {
            "brakeman_version": "5.4.1",
            "security_warnings": 0
        },
        "warnings": [],
        "ignored_warnings": [],
        "errors": []
    }


def test_parser_initialization(brakeman_parser):
    """Test that the parser initializes correctly."""
    assert brakeman_parser.tool_name == "brakeman"

    # Check field mapping
    expected_mapping = {
        "rule_id": "warning_code",
        "code": "code",
        "severity": "severity",
        "confidence": "confidence",
        "message": "message",
        "path": "file",
        "start_line": "line",
        "end_line": "line",
        "issue_metadata": "metadata"
    }
    assert brakeman_parser.field_mapping == expected_mapping


def test_parse_minimal_output(brakeman_parser, minimal_brakeman_output):
    """Test parsing minimal valid Brakeman output."""
    result = brakeman_parser.parse_scan_result(minimal_brakeman_output)

    assert len(result.issues) == 1
    assert result.summary["total"] == 1

    issue = result.issues[0]
    assert issue.rule_id == "1"
    assert issue.message == "Test message"
    assert issue.path == "test.rb"
    assert issue.start_line == 1


@pytest.mark.parametrize("confidence_level,expected_severity", [
    ("High", AnalyticQSeverity.HIGH),
    ("Medium", AnalyticQSeverity.MEDIUM),
    ("Low", AnalyticQSeverity.LOW),
    ("Unknown", AnalyticQSeverity.UNKNOWN),
    ("InvalidLevel", AnalyticQSeverity.UNKNOWN),
])
def test_severity_mapping(brakeman_parser, confidence_level, expected_severity):
    """Test severity level mapping with parametrization.

    Note: Brakeman uses confidence levels which are mapped to severity in this parser.
    """
    assert brakeman_parser._map_severity(confidence_level) == expected_severity


@pytest.mark.parametrize("confidence_level,expected_confidence", [
    ("High", AnalyticQConfidence.HIGH),
    ("Medium", AnalyticQConfidence.MEDIUM),
    ("Low", AnalyticQConfidence.LOW),
    ("Weak", AnalyticQConfidence.LOW),
    ("Unknown", AnalyticQConfidence.UNKNOWN),
    ("InvalidLevel", AnalyticQConfidence.UNKNOWN),
])
def test_confidence_mapping(brakeman_parser, confidence_level, expected_confidence):
    """Test confidence level mapping with parametrization."""
    assert brakeman_parser._map_confidence(confidence_level) == expected_confidence


def test_scan_metadata_extraction(brakeman_parser, sample_brakeman_output):
    """Test that scan metadata is properly extracted."""
    result = brakeman_parser.parse_scan_result(sample_brakeman_output)

    metadata = result.scan_metadata
    assert metadata["brakeman_version"] == "5.4.1"
    assert metadata["rails_version"] == "7.0.4"
    assert metadata["ruby_version"] == "3.1.0"
    assert metadata["start_time"] == "2023-01-01 12:00:00 +0000"
    assert metadata["end_time"] == "2023-01-01 12:00:30 +0000"
    assert metadata["duration"] == 30.5
    assert metadata["security_warnings"] == 3
    assert metadata["number_of_controllers"] == 5
    assert metadata["number_of_models"] == 8
    assert metadata["number_of_templates"] == 12

    # Check checks_performed
    expected_checks = ["BasicAuth", "CrossSiteScripting", "SQL", "Command", "Evaluation"]
    assert metadata["checks_performed"] == expected_checks

    # Check metrics
    metrics = metadata["metrics"]
    assert metrics["total_warnings"] == 3
    assert metrics["ignored_warnings"] == 1
    assert metrics["errors"] == 0


def test_transform_output(brakeman_parser, sample_brakeman_output):
    """Test the transform_output method specifically."""
    transformed = brakeman_parser.transform_output(sample_brakeman_output)

    assert len(transformed) == 3

    # Check first transformed issue
    first_issue = transformed[0]
    assert first_issue["warning_code"] == "2"
    assert first_issue["warning_type"] == "Cross-Site Scripting"
    assert first_issue["code"] == "<%= @user.name %>"
    assert first_issue["file"] == "app/views/users/show.html.erb"
    assert first_issue["message"] == "Unescaped model attribute"
    assert first_issue["line"] == 15
    assert first_issue["confidence"] == "High"
    assert first_issue["location_type"] == "template"

    # Check metadata
    metadata = first_issue["metadata"]
    assert metadata["user_input"] == "@user.name"
    assert metadata["link"] == "https://brakemanscanner.org/docs/warning_types/cross_site_scripting/"
    assert metadata["cwe_id"] == [79]


def test_parse_scan_result_with_null_arrays(brakeman_parser):
    """Test parsing when ignored_warnings or errors are null."""
    output_with_nulls = {
        "scan_info": {"brakeman_version": "5.4.1"},
        "warnings": [],
        "ignored_warnings": None,
        "errors": None
    }

    result = brakeman_parser.parse_scan_result(output_with_nulls)

    # Should handle null arrays gracefully
    metrics = result.scan_metadata["metrics"]
    assert metrics["total_warnings"] == 0
    assert metrics["ignored_warnings"] == 0
    assert metrics["errors"] == 0


def test_parse_scan_result_exception_handling(brakeman_parser):
    """Test that parsing exceptions are properly wrapped."""
    invalid_output = "not a dictionary"

    with pytest.raises(ScanParserException) as exc_info:
        brakeman_parser.parse_scan_result(invalid_output)

    assert "Unexpected error parsing Brakeman results" in str(exc_info.value)


def test_parse_scan_result(brakeman_parser, sample_brakeman_output, monkeypatch):
    """Test parsing of complete Brakeman scan results."""
    mock_datetime = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("analyticq.engine.core.models.datetime", lambda: mock_datetime)

    result = brakeman_parser.parse_scan_result(sample_brakeman_output)

    # Check basic result structure
    assert len(result.issues) == 3
    assert result.summary["total"] == 3
    assert result.scan_metadata["tool_name"] == "brakeman"

    # Check first issue (XSS)
    first_issue = result.issues[0]
    assert first_issue.rule_id == "2"
    assert first_issue.severity == AnalyticQSeverity.UNKNOWN
    assert first_issue.confidence == AnalyticQConfidence.HIGH
    assert first_issue.path == "app/views/users/show.html.erb"
    assert first_issue.start_line == 15
    assert first_issue.end_line == 15
    assert first_issue.message == "Unescaped model attribute"
    assert first_issue.code == "<%= @user.name %>"

    # Check second issue (SQL Injection)
    second_issue = result.issues[1]
    assert second_issue.rule_id == "0"
    assert second_issue.severity == AnalyticQSeverity.UNKNOWN
    assert second_issue.confidence == AnalyticQConfidence.MEDIUM
    assert second_issue.path == "app/models/user.rb"
    assert second_issue.start_line == 25
    assert second_issue.message == "Possible SQL injection"

    # Check third issue (Dangerous Evaluation)
    third_issue = result.issues[2]
    assert third_issue.rule_id == "13"
    assert third_issue.severity == AnalyticQSeverity.UNKNOWN
    assert third_issue.confidence == AnalyticQConfidence.HIGH
    assert third_issue.path == "app/controllers/admin_controller.rb"
    assert third_issue.start_line == 42
