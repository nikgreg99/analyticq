from datetime import datetime

import pytest
from analyticq.service import AnalyticQIDGeneratorService, AnalyticQScanContext


@pytest.fixture
def mock_scan_context():
    return AnalyticQScanContext(
        path="/path/to/test-repo",
        repo_name="test-repo",
        branch="dev",
        last_commit_hash="a1b2c3d4e5f6g7h8"
    )


@pytest.fixture
def id_generator_service():
    return AnalyticQIDGeneratorService()


def test_scan_id_format(id_generator_service, mock_scan_context):
    """Test that generated scan ID follows the expected format"""
    scan_id = id_generator_service.generate_scan_id(mock_scan_context)

    # Split into components
    parts = scan_id.split("-")

    assert len(parts) == 4, "Scan ID should have 4 parts separated by hyphens"
    assert parts[0] == "S", "Should start with default prefix"
    assert len(parts[1]) == 12, "Codebase ID should be 12 characters"
    assert parts[2] == "a1b2c3d", "Source ID should be first 7 chars of commit hash"
    assert len(parts[3]) == 14, "Timestamp should be 14 digits"

    # Verify timestamp format
    timestamp_str = parts[3]
    timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
    assert isinstance(timestamp, datetime)


def test_parse_scan_id(id_generator_service, mock_scan_context):
    """Test that scan ID can be correctly parsed back into components"""
    scan_id = id_generator_service.generate_scan_id(mock_scan_context)
    parsed = id_generator_service.parse_scan_id(scan_id)

    assert isinstance(parsed, dict)
    assert parsed['prefix'] == 'S', "Should have correct prefix"
    assert len(parsed['codebase_id']) == 12, "Should have 12-char codebase ID"
    assert parsed['source_id'] == "a1b2c3d", "Should have correct source ID"
    assert isinstance(parsed['timestamp'], datetime), "Should parse timestamp to datetime"


def test_generate_scan_id_without_commit(id_generator_service):
    context = AnalyticQScanContext(
        path="/path/to/test-repo",
        repo_name="test-repo"
    )

    scan_id = id_generator_service.generate_scan_id(context)
    id_parts = scan_id.split("-")

    assert len(id_parts) == 4
    assert len(id_parts[2]) == 7, "Should generate 7-char source ID hash"


def test_codebase_id_constistency(id_generator_service):
    context1 = AnalyticQScanContext(
        path="/path/to/test-repo",
        repo_name="test-repo"
    )

    context2 = AnalyticQScanContext(
        path="/path/to/test-repo",
        repo_name="test-repo"
    )

    id1 = id_generator_service.generate_codebase_id(context1)
    id2 = id_generator_service.generate_codebase_id(context2)

    assert id1 == id2, "Same context should produce same codebase ID"
    assert len(id1) == len(id2), "Codebase ID should be of the same length"


def test_deterministic_issue_id(id_generator_service, mock_scan_context):
    scan_id = id_generator_service.generate_scan_id(mock_scan_context)
    finding_details = "Critical security vulnerability"

    issue_id_1 = id_generator_service.generate_issue_id(scan_id, finding_details)
    issue_id_2 = id_generator_service.generate_issue_id(scan_id, finding_details)

    assert issue_id_1 == issue_id_2, "Expected to be equal"


def test_invalid_scan_id_parsing(id_generator_service):
    with pytest.raises(ValueError):
        id_generator_service.parse_scan_id("invalid-format")


def test_different_repo_scan_ids(id_generator_service):

    context_1 = AnalyticQScanContext(
        repo_name="repo1",
        last_commit_hash="a1b2c3d",
        branch="dev"
    )

    context_2 = AnalyticQScanContext(
        repo_name="repo2",
        last_commit_hash="a1b2c3d",
        branch="dev"
    )

    scan_id_1 = id_generator_service.generate_scan_id(context_1)
    scan_id_2 = id_generator_service.generate_scan_id(context_2)

    assert scan_id_1 != scan_id_2, "Expected scan_id to be different"
