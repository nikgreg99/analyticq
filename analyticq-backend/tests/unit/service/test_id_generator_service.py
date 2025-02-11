from datetime import datetime

import pytest
from analyticq.service import AnalyticQIDGeneratorService, AnalyticQScanContext


@pytest.fixture
def mock_scan_context():
    return AnalyticQScanContext(
        repo_name="test-repo",
        branch="dev",
        last_commit_hash="a1b2c3d4e5f6g7h8",
    )


@pytest.fixture
def id_generator_service():
    return AnalyticQIDGeneratorService()


def test_scan_id_format(id_generator_service, mock_scan_context):
    scan_id = id_generator_service.generate_scan_id(mock_scan_context)
    assert scan_id.startswith("S"), "Expected start with default prefix"

    parts = scan_id.split("-")
    assert len(parts) == 4, "Expected 4 parts for this id"
    assert parts[1] == "testrepo"
    assert len(parts[2]) == 7  # commit short hash
    assert len(parts[3]) == 14  # timestamp


def test_parse_scan_id(id_generator_service, mock_scan_context):
    scan_id = id_generator_service.generate_scan_id(mock_scan_context)
    parsed = id_generator_service.parse_scan_id(scan_id)

    assert parsed['prefix'] == 'S'
    assert parsed['repo'] == 'testrepo'
    assert len(parsed['commit_short']) == 7
    assert isinstance(parsed['timestamp'], datetime)


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
