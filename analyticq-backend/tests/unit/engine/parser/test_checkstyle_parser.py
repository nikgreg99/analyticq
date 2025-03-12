from typing import Any, Dict

import pytest
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.engine.parser import CheckStyleParser


@pytest.fixture
def sample_sarif_data() -> Dict[str, Any]:
    """Fixture providing sample Checkstyle SARIF data for testing."""
    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "downloadUri": "https://github.com/checkstyle/checkstyle/releases/",
                    "fullName": "Checkstyle",
                    "informationUri": "https://checkstyle.org/",
                    "language": "en",
                    "name": "Checkstyle",
                    "organization": "Checkstyle",
                    "rules": [
                        {
                            "id": "javadoc.missing",
                            "shortDescription": {"text": "Missing Javadoc comment"},
                            "helpUri": "https://checkstyle.org/config_javadoc.html"
                        },
                        {
                            "id": "maxLineLen",
                            "shortDescription": {"text": "Line is longer than allowed limit"},
                            "helpUri": "https://checkstyle.org/config_sizes.html"
                        }
                    ],
                    "semanticVersion": "10.21.4",
                    "version": "10.21.4"
                }
            },
            "results": [
                {
                    "level": "error",
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": "file:/code/src/main/java/com/example/app/App.java"},
                            "region": {"startLine": 1}
                        }
                    }],
                    "message": {"text": "Missing package-info.java file."},
                    "ruleId": "javadoc.packageInfo"
                },
                {
                    "level": "error",
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": "file:/code/src/main/java/com/example/app/App.java"},
                            "region": {"startColumn": 17, "startLine": 4}
                        }
                    }],
                    "message": {"text": "Using the '.*' form of import should be avoided - java.util.*."},
                    "ruleId": "import.avoidStar"
                },
                {
                    "level": "error",
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": "file:/code/src/main/java/com/example/app/App.java"},
                            "region": {"startLine": 11}
                        }
                    }],
                    "message": {"text": "Line is longer than 80 characters (found 143)."},
                    "ruleId": "maxLineLen"
                }
            ]
        }]
    }


@pytest.fixture
def empty_sarif_data() -> Dict[str, Any]:
    """Fixture providing SARIF data with no results."""
    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "Checkstyle",
                    "version": "10.21.4"
                }
            },
            "results": []
        }]
    }


@pytest.fixture
def checkstyle_parser() -> CheckStyleParser:
    """Fixture providing a CheckstyleParser instance."""
    return CheckStyleParser()


def test_initialization(checkstyle_parser):
    """Test that parser initializes with the correct values."""
    assert checkstyle_parser.tool_name == "checkstyle"
    assert "rule_id" in checkstyle_parser.field_mapping
    assert "message" in checkstyle_parser.field_mapping
    assert "path" in checkstyle_parser.field_mapping
    assert "start_line" in checkstyle_parser.field_mapping
    assert "severity" in checkstyle_parser.field_mapping


def test_severity_mapping(checkstyle_parser):
    assert checkstyle_parser._map_severity("error") == AnalyticQSeverity.MEDIUM
    assert checkstyle_parser._map_severity("warning") == AnalyticQSeverity.LOW
    assert checkstyle_parser._map_severity("info") == AnalyticQSeverity.INFO
    assert checkstyle_parser._map_severity("unknown") == AnalyticQSeverity.UNKNOWN


def test_confidence_mapping(checkstyle_parser):
    assert checkstyle_parser._map_confidence("any_value") == AnalyticQConfidence.UNKNOWN


def test_rule_categorization(checkstyle_parser):
    """Test rule categorization method."""
    assert checkstyle_parser._categorize_checkstyle_rule("javadoc.missing") == "Documentation"
    assert checkstyle_parser._categorize_checkstyle_rule("maxLineLen") == "Code Style"
    assert checkstyle_parser._categorize_checkstyle_rule("name.invalidPattern") == "Naming Convention"
    assert checkstyle_parser._categorize_checkstyle_rule("unknown.rule") == "Other"


def test_extract_rule_details(checkstyle_parser, sample_sarif_data):
    """Test extraction of rule details from SARIF data."""
    rule_details = checkstyle_parser._extract_rule_details(sample_sarif_data)

    assert "javadoc.missing" in rule_details
    assert "maxLineLen" in rule_details
    assert rule_details["javadoc.missing"]["description"] == "Missing Javadoc comment"
    assert rule_details["maxLineLen"]["help_uri"] == "https://checkstyle.org/config_sizes.html"


def test_extract_rule_details_empty(checkstyle_parser):
    """Test extraction of rule details with missing data."""
    empty_data = {"runs": [{"tool": {"driver": {}}}]}
    rule_details = checkstyle_parser._extract_rule_details(empty_data)
    assert rule_details == {}
    no_rules_data = {"runs": [{"tool": {"driver": {"rules": []}}}]}
    rule_details = checkstyle_parser._extract_rule_details(no_rules_data)
    assert rule_details == {}


def test_extract_location_info(checkstyle_parser):
    """Test extraction of location information."""
    result = {
        "locations": [{
            "physicalLocation": {
                "artifactLocation": {"uri": "test.java"},
                "region": {"startLine": 10, "startColumn": 5}
            }
        }]
    }

    location = checkstyle_parser._extract_location_info(result)
    assert location["uri"] == "test.java"
    assert location["startLine"] == 10
    assert location["startColumn"] == 5
    assert location["endLine"] == 10  # Default to startLine if endLine not provided


def test_transform_sarif_to_issues(checkstyle_parser, sample_sarif_data):
    """Test transformation of SARIF data to issues."""
    transformed = checkstyle_parser.transform_sarif_to_issues(sample_sarif_data)

    assert len(transformed) == 3
    assert transformed[0]["ruleId"] == "javadoc.packageInfo"
    assert transformed[1]["ruleId"] == "import.avoidStar"
    assert transformed[2]["ruleId"] == "maxLineLen"

    # Verify the transformation preserved the message texts
    assert "Missing package-info.java file." in transformed[0]["message"]["text"]
    assert "Using the '.*' form of import should be avoided" in transformed[1]["message"]["text"]
    assert "Line is longer than 80 characters" in transformed[2]["message"]["text"]


def test_transform_single_issue(checkstyle_parser):
    """Test transformation of a single issue."""
    rule_details = {
        "javadoc.missing": {
            "description": "Missing Javadoc comment",
            "help_uri": "https://checkstyle.org/config_javadoc.html",
            "tags": []
        }
    }

    result = {
        "ruleId": "javadoc.missing",
        "message": {"text": "Missing a Javadoc comment."},
        "level": "error",
        "locations": [{
            "physicalLocation": {
                "artifactLocation": {"uri": "file:/code/src/main/java/com/example/app/App.java"},
                "region": {"startLine": 5, "startColumn": 9}
            }
        }]
    }

    transformed = checkstyle_parser._transform_single_issue(result, rule_details)

    assert transformed["ruleId"] == "javadoc.missing"
    assert transformed["message"]["text"] == "Missing a Javadoc comment."
    assert transformed["level"] == "error"
    assert transformed["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "file:/code/src/main/java/com/example/app/App.java"
    assert transformed["locations"][0]["physicalLocation"]["region"]["startLine"] == 5
    assert transformed["locations"][0]["physicalLocation"]["region"]["startColumn"] == 9
    assert transformed["metadata"]["category"] == "Documentation"
    assert transformed["metadata"]["rule_description"] == "Missing Javadoc comment"


def test_transform_empty_sarif(checkstyle_parser, empty_sarif_data):
    """Test transformation of SARIF data with no results."""
    transformed = checkstyle_parser.transform_sarif_to_issues(empty_sarif_data)
    assert len(transformed) == 0
