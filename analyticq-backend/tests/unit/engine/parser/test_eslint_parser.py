from datetime import UTC, datetime
from typing import Dict, List

import pytest
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.engine.parser import ESLintParser


@pytest.fixture
def eslint_parser():
    return ESLintParser()


@pytest.fixture
def sample_eslint_output() -> List[Dict]:
    """Sample ESLint output for testing.
    Format based on ESLint JSON output format.
    # Link reference https://eslint.org/docs/latest/use/formatters/#json
    """
    return [
        {
            "filePath": "/var/lib/jenkins/workspace/eslint Release/eslint/fullOfProblems.js",
            "messages": [
                {
                    "ruleId": "no-unused-vars",
                    "severity": 2,
                    "message": "'addOne' is defined but never used.",
                    "line": 1,
                    "column": 10,
                    "nodeType": "Identifier",
                    "messageId": "unusedVar",
                    "endLine": 1,
                    "endColumn": 16,
                    "suggestions": [
                        {
                            "messageId": "removeVar",
                            "data": {
                                "varName": "addOne"
                            },
                            "fix": {
                                "range": [0, 94],
                                "text": ""
                            },
                            "desc": "Remove unused variable 'addOne'."
                        }
                    ]
                },
                {
                    "ruleId": "use-isnan",
                    "severity": 2,
                    "message": "Use the isNaN function to compare with NaN.",
                    "line": 2,
                    "column": 9,
                    "nodeType": "BinaryExpression",
                    "messageId": "comparisonWithNaN",
                    "endLine": 2,
                    "endColumn": 17,
                    "suggestions": [
                        {
                            "messageId": "replaceWithIsNaN",
                            "fix": {
                                "range": [29, 37],
                                "text": "!Number.isNaN(i)"
                            },
                            "desc": "Replace with Number.isNaN."
                        }
                    ]
                },
                {
                    "ruleId": "semi",
                    "severity": 1,
                    "message": "Missing semicolon.",
                    "line": 3,
                    "column": 20,
                    "nodeType": "ReturnStatement",
                    "messageId": "missingSemi",
                    "endLine": 4,
                    "endColumn": 1,
                    "fix": {
                        "range": [60, 60],
                        "text": ";"
                    }
                }
            ],
            "suppressedMessages": [],
            "errorCount": 2,
            "fatalErrorCount": 0,
            "warningCount": 1,
            "fixableErrorCount": 1,
            "fixableWarningCount": 1,
            "source": "function addOne(i) {\n    if (i != NaN) {\n        return i ++\n    } else {\n      return\n    }\n};"
        }
    ]


def test_parser_initialization(eslint_parser):
    """Test that the parser initializes correctly."""
    assert eslint_parser.tool_name == "eslint", "Exptected eslint as tool name"
    assert eslint_parser.field_mapping["rule_id"] == "ruleId"
    assert eslint_parser.field_mapping["message"] == "message"
    assert eslint_parser.field_mapping["severity"] == "severity"
    assert eslint_parser.field_mapping["path"] == "filePath"


def test_parse_scan_result(eslint_parser, sample_eslint_output, monkeypatch):
    """Test the full parsing of ESLint output."""
    # Mock datetime.now() to return a consistent timestamp
    mock_date = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("datetime.datetime", lambda tz: mock_date)

    result = eslint_parser.parse_scan_result(sample_eslint_output)

    # Check that we have the correct number of issues
    assert len(result.issues) == 3

    # Check first issue (no-unused-vars)
    first_issue = result.issues[0]
    assert first_issue.rule_id == "no-unused-vars"
    assert first_issue.severity == AnalyticQSeverity.HIGH
    assert first_issue.confidence == AnalyticQConfidence.UNKNOWN
    assert first_issue.path == "/var/lib/jenkins/workspace/eslint Release/eslint/fullOfProblems.js"
    assert first_issue.start_line == 1
    assert first_issue.end_line == 1
    assert first_issue.message == "'addOne' is defined but never used."
    assert "suggestions" in first_issue.metadata

    # Check second issue (use-isnan)
    second_issue = result.issues[1]
    assert second_issue.rule_id == "use-isnan"
    assert second_issue.severity == AnalyticQSeverity.HIGH
    assert second_issue.message == "Use the isNaN function to compare with NaN."
    assert second_issue.start_line == 2

    # Check third issue (semi)
    third_issue = result.issues[2]
    assert third_issue.rule_id == "semi"
    assert third_issue.severity == AnalyticQSeverity.MEDIUM
    assert third_issue.message == "Missing semicolon."

    # Check metadata
    assert result.metadata["tool_name"] == "eslint"
    assert result.metadata["files_analyzed"] == 1
    assert result.metadata["total_errors"] == 2
    assert result.metadata["total_warnings"] == 1
    assert result.metadata["total_fixable_errors"] == 1
    assert result.metadata["total_fixable_warnings"] == 1


def test_transform_output(eslint_parser, sample_eslint_output):
    """Test that the transform_output method correctly transforms ESLint output."""
    transformed = eslint_parser.transform_output(sample_eslint_output)
    assert len(transformed) == 3

    # Check that the transformation preserves key fields
    first_transformed = transformed[0]
    assert first_transformed["ruleId"] == "no-unused-vars"
    assert first_transformed["severity"] == 2
    assert first_transformed["line"] == 1
    assert first_transformed["endLine"] == 1
    assert "metadata" in first_transformed
    assert "suggestions" in first_transformed["metadata"]


@pytest.mark.parametrize("severity_level,expected_severity", [
    (0, AnalyticQSeverity.INFO),
    (1, AnalyticQSeverity.MEDIUM),
    (2, AnalyticQSeverity.HIGH),
    ("0", AnalyticQSeverity.INFO),
    ("1", AnalyticQSeverity.MEDIUM),
    ("2", AnalyticQSeverity.HIGH),
    ("unknown", AnalyticQSeverity.UNKNOWN),
])
def test_severity_mapping(eslint_parser, severity_level, expected_severity):
    """Test severity level mapping with parametrization."""
    assert eslint_parser._map_severity(severity_level) == expected_severity


def test_confidence_mapping(eslint_parser):
    """Test that confidence mapping returns UNKNOWN for any input."""
    assert eslint_parser._map_confidence("any_value") == AnalyticQConfidence.UNKNOWN


def test_parse_empty_output(eslint_parser):
    """Test parsing an empty ESLint output."""
    empty_eslint_output = []

    result = eslint_parser.parse_scan_result(empty_eslint_output)
    assert len(result.issues) == 0
    assert result.summary["total"] == 0
    assert result.metadata["tool_name"] == "eslint"
    assert result.metadata["total_errors"] == 0
    assert result.metadata["total_warnings"] == 0


def test_parse_output_with_no_messages(eslint_parser):
    """Test parsing ESLint output with files but no messages."""
    eslint_output_no_messages = [
        {
            "filePath": "/path/to/clean/file.js",
            "messages": [],
            "errorCount": 0,
            "warningCount": 0,
            "fixableErrorCount": 0,
            "fixableWarningCount": 0,
            "source": "const x = 5;"
        }
    ]

    result = eslint_parser.parse_scan_result(eslint_output_no_messages)
    assert len(result.issues) == 0
    assert result.metadata["total_errors"] == 0
    assert result.metadata["files_analyzed"] == 1
