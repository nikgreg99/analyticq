import csv
import tempfile

import pytest
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.engine.parser import FlawFinderParser
from analyticq.exception import ScanParserException


@pytest.fixture
def sample_csv_file() -> str:
    """Create a temporary CSV file and return its path."""
    csv_content = '''File,Line,Column,DefaultLevel,Level,Category,Name,Warning,Suggestion,Note,CWEs,Context,Fingerprint,ToolVersion,RuleId,HelpUri
sample.c,8,5,5,5,buffer,gets,"Buffer overflow risk","Use fgets() instead",,"CWE-120,CWE-20","gets(buffer);",92d53362835b,2.0.19,FF1014,https://example.com/120
sample.c,32,5,4,4,shell,system,"Shell injection risk","Use library calls",,CWE-78,"system(cmd);",dc4d9818f2fa,2.0.19,FF1044,https://example.com/78'''

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".csv")
    temp_file.write(csv_content)
    temp_file.close()
    return temp_file.name


@pytest.fixture
def flawfinder_parser() -> FlawFinderParser:
    return FlawFinderParser()


@pytest.fixture
def csv_data(sample_csv_file) -> str:
    """Read CSV content once for reuse."""
    with open(sample_csv_file, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        data = [row for row in reader]
    return data


def test_successful_parse(flawfinder_parser, csv_data):

    """Test successful parsing of FlawFinder results."""
    result = flawfinder_parser.parse_scan_result(csv_data)

    assert result.scan_id is not None
    assert len(result.issues) == 2
    assert result.summary["total"] == 2

    issue = result.issues[0]
    assert issue.path == "sample.c"
    assert issue.start_line == 8
    assert issue.severity == AnalyticQSeverity.CRITICAL
    assert issue.confidence == AnalyticQConfidence.UNKNOWN
    assert "buffer" in issue.message.lower()
    assert issue.issue_metadata["cwes"] == ["CWE-120", "CWE-20"]


def test_metadata_handling(flawfinder_parser, csv_data):
    result = flawfinder_parser.parse_scan_result(csv_data)

    assert result.scan_metadata["tool_name"] == "FlawFinder"
    issue = result.issues[0]
    assert "category" in issue.issue_metadata
    assert "cwes" in issue.issue_metadata
    assert "help_uri" in issue.issue_metadata


def test_parser_initialization(flawfinder_parser):
    """Test parser initialization and tool name."""
    assert flawfinder_parser.tool_name == "FlawFinder"
    assert flawfinder_parser.field_mapping == {
        "rule_id": "RuleId",
        "message": "Warning",
        "path": "File",
        "start_line": "Line",
        "end_line": "Line",
        "severity": "Level",
        "code": "Context",
        "issue_metadata": "Metadata"
    }


def test_malformed_csv(flawfinder_parser):
    malformed_input = '''File,Line,Column
bad,data,format,extra,columns
'''
    with pytest.raises(ScanParserException):
        flawfinder_parser.parse_scan_result(malformed_input)


def test_severity_mapping(flawfinder_parser):
    assert flawfinder_parser._map_severity("1") == AnalyticQSeverity.LOW
    assert flawfinder_parser._map_severity("2") == AnalyticQSeverity.LOW
    assert flawfinder_parser._map_severity("3") == AnalyticQSeverity.MEDIUM
    assert flawfinder_parser._map_severity("4") == AnalyticQSeverity.HIGH
    assert flawfinder_parser._map_severity("5") == AnalyticQSeverity.CRITICAL
    assert flawfinder_parser._map_severity("6") == AnalyticQSeverity.UNKNOWN


def test_confidence_mapping(flawfinder_parser):
    assert flawfinder_parser._map_confidence("any") == AnalyticQConfidence.UNKNOWN


def test_missing_required_field(flawfinder_parser):
    incomplete_data = '''File,Line
    sample.c,1'''

    with pytest.raises(ScanParserException):
        flawfinder_parser.parse_scan_result(incomplete_data)
