from datetime import UTC, datetime
from typing import Dict

import pytest
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.engine.parser import RubocopParser


@pytest.fixture
def rubocop_parser():
    return RubocopParser()


@pytest.fixture
def sample_rubocop_output() -> Dict:
    """Sample RuboCop output for testing.
    Format: https://docs.rubocop.org/rubocop/formatters.html#json-formatter
    """
    return {
        "metadata": {
            "rubocop_version": "1.12.0",
            "ruby_engine": "ruby",
            "ruby_version": "3.0.0",
            "ruby_patchlevel": "0",
            "ruby_platform": "x86_64-darwin19"
        },
        "files": [
            {
                "path": "lib/foo.rb",
                "offenses": []
            },
            {
                "path": "lib/bar.rb",
                "offenses": [
                    {
                        "severity": "convention",
                        "message": "Line is too long. [81/80]",
                        "cop_name": "LineLength",
                        "corrected": True,
                        "location": {
                            "line": 546,
                            "column": 80,
                            "length": 4
                        }
                    },
                    {
                        "severity": "warning",
                        "message": "Unreachable code detected.",
                        "cop_name": "UnreachableCode",
                        "corrected": False,
                        "location": {
                            "line": 15,
                            "column": 9,
                            "length": 10
                        }
                    }
                ]
            }
        ],
        "summary": {
            "offense_count": 2,
            "target_file_count": 2,
            "inspected_file_count": 2
        }
    }


def test_parser_initialization(rubocop_parser):
    """Test that the parser initializes correctly."""
    assert rubocop_parser.tool_name == "rubocop"
    assert rubocop_parser.field_mapping["rule_id"] == "rule_id"
    assert rubocop_parser.field_mapping["severity"] == "severity"


def test_parse_scan_result(rubocop_parser, sample_rubocop_output, monkeypatch):
    mock_date_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("datetime.datetime", mock_date_now)

    result = rubocop_parser.parse_scan_result(sample_rubocop_output)

    assert len(result.issues) == 2

    # Check first issue
    first_issue = result.issues[0]
    assert first_issue.rule_id == "LineLength"
    assert first_issue.severity == AnalyticQSeverity.LOW
    assert first_issue.confidence == AnalyticQConfidence.UNKNOWN
    assert first_issue.path == "lib/bar.rb"
    assert first_issue.start_line == 546
    assert first_issue.message == "Line is too long. [81/80]"

    # Check second issue
    second_issue = result.issues[1]
    assert second_issue.rule_id == "UnreachableCode"
    assert second_issue.severity == AnalyticQSeverity.MEDIUM
    assert second_issue.confidence == AnalyticQConfidence.UNKNOWN
    assert second_issue.message == "Unreachable code detected."


@pytest.mark.parametrize("severity_level,expected_severity", [
    ("info", AnalyticQSeverity.INFO),
    ("refactor", AnalyticQSeverity.LOW),
    ("convention", AnalyticQSeverity.LOW),
    ("warning", AnalyticQSeverity.MEDIUM),
    ("error", AnalyticQSeverity.HIGH),
    ("fatal", AnalyticQSeverity.CRITICAL),
    ("unknown", AnalyticQSeverity.UNKNOWN),
])
def test_severity_mapping(rubocop_parser, severity_level, expected_severity):
    """Test severity level mapping with parametrization."""
    assert rubocop_parser._map_severity(severity_level) == expected_severity


def test_confidence_mapping(rubocop_parser):
    assert rubocop_parser._map_confidence("unknown") == AnalyticQConfidence.UNKNOWN


def test_parse_empty_output(rubocop_parser):
    empty_rubocop_output = {
        "metadata": {
            "rubocop_version": "1.12.0"
        },
        "files": [],
        "summary": {
            "offense_count": 0,
            "target_file_count": 0,
            "inspected_file_count": 0
        }
    }

    result = rubocop_parser.parse_scan_result(empty_rubocop_output)
    assert len(result.issues) == 0
    assert result.summary["total"] == 0
    assert result.metadata["tool_name"] == "rubocop"
