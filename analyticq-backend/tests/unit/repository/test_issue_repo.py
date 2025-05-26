import os
from pathlib import Path

import pytest
from analyticq.config import AnalyticQBaseConfig, AnalyticQEnvironmentLoader
from analyticq.engine import AnalyticQConfidence, AnalyticQSeverity
from analyticq.manager.db_manager import AnalyticQDatabaseManager
from analyticq.repository.context_repository import \
    AnalyticQContextRepository  # noqa
from analyticq.repository.issue_repository import (  # noqa
    AnalyticQSASTIssue, AnalyticQSASTIssueModel, AnalyticQSASTIssueRepository)
from analyticq.repository.scan_repository import \
    AnalyticQScanResultRepository  # noqa
from analyticq.repository.stats_repository import \
    AnalyticQStatsRepository  # noqa
from sqlalchemy import text

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent


@pytest.fixture
def issue_repo():
    return AnalyticQSASTIssueRepository()


@pytest.fixture(autouse=True)
async def setup_db():
    """
    Set up the database schema before each test and tear it down afterward.
    """
    # Use absolute paths based on the project structure
    test_file = BASE_DIR / "unit" / "test_files"
    print(f"Config directory path: {test_file}")
    AnalyticQBaseConfig.load_config_file(str(test_file), "test_config.json")

    test_env_file = BASE_DIR / "unit" / "test_files" / ".env.test"
    print(f"Environment file path: {test_env_file}")

    AnalyticQEnvironmentLoader.load(test_env_file, "test")
    db_manager = AnalyticQDatabaseManager()
    await db_manager.init_db()

    # Disable foreign key constraints for SQLite
    async with db_manager.get_db_session() as session:
        await session.execute(text("PRAGMA foreign_keys=OFF"))
        await session.commit()

    yield

    # Clean up the database after tests
    async with db_manager.get_db_session() as session:
        await session.execute(text("DELETE FROM analyticq_sast_issues"))
        await session.commit()

    await db_manager.close()

# Test data
TEST_ISSUE_DATA = {
    "rule_id": "rule_456",
    "scan_id": 1,
    "severity": AnalyticQSeverity.HIGH,
    "confidence": AnalyticQConfidence.HIGH,
    "code": "print('Hello, World!')",
    "message": "Potential security issue",
    "path": "/path/to/file.py",
    "start_line": 10,
    "end_line": 10,
    "column": 5,
    "issue_metadata": {"key": "value"},
    "summary": {"key": "value"},
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
}

# Test data
TEST_ISSUE_DATA_2 = {
    "rule_id": "rule_456",
    "scan_id": 1,
    "severity": AnalyticQSeverity.HIGH,
    "confidence": AnalyticQConfidence.HIGH,
    "code": "print('Hello, World!')",
    "message": "Potential security issue",
    "path": "/path/to/file.py",
    "start_line": 10,
    "end_line": 10,
    "column": 5,
    "issue_metadata": {"key": "value"},
    "summary": {"key": "value"},
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
}

TEST_UPDTATED_ISSUE_DATA = {
    "id": 1,
    "scan_id": 1,
    "rule_id": "rule_456",
    "severity": AnalyticQSeverity.MEDIUM,
    "confidence": AnalyticQConfidence.HIGH,
    "code": "print('Hello, World!')",
    "message": "Potential security issue",
    "path": "/path/to/file.py",
    "start_line": 10,
    "end_line": 10,
    "column": 5,
    "issue_metadata": {"key": "value"},
    "summary": {"key": "value"},
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
}


# Test cases
@pytest.mark.asyncio
async def test_add_issue(issue_repo):
    issue = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)
    # Add the issue to the database
    await issue_repo.add_issue(issue)


@pytest.mark.asyncio
async def test_get_issue_by_id(issue_repo):
    # Add an issue to the database
    issue = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)
    await issue_repo.add_issue(issue)

    # Retrieve the issue by ID
    retrieved_issue = await issue_repo.get_issue_by_id(1)
    assert retrieved_issue is not None
    assert retrieved_issue.rule_id == "rule_456"


@pytest.mark.asyncio
async def test_add_issue_missing_scan_id(issue_repo):
    # Create an issue without a scan_id
    issue_data = {**TEST_ISSUE_DATA, "scan_id": None}
    issue = AnalyticQSASTIssueModel(**issue_data)

    # Ensure a ValueError is raised
    with pytest.raises(ValueError, match="scan_id is required for AnalyticQSASTIssue"):
        await issue_repo.add_issue(issue)


@pytest.mark.asyncio
async def test_update_issue_by_id(issue_repo):
    # Add an issue to the database
    issue = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)
    await issue_repo.add_issue(issue)

    # Update the issue
    await issue_repo.update_issue_by_id(1, AnalyticQSASTIssueModel(**TEST_UPDTATED_ISSUE_DATA))

    # Verify the update
    updated_issue = await issue_repo.get_issue_by_id(1)
    assert updated_issue.severity == AnalyticQSeverity.MEDIUM


@pytest.mark.asyncio
async def test_filter_scan_issues(issue_repo):
    # Add multiple issues with different severities and confidences
    issue1 = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)
    issue2 = AnalyticQSASTIssueModel(**{**TEST_ISSUE_DATA, "severity": AnalyticQSeverity.MEDIUM, "confidence": AnalyticQConfidence.MEDIUM})
    issue3 = AnalyticQSASTIssueModel(**{**TEST_ISSUE_DATA, "severity": AnalyticQSeverity.LOW, "confidence": AnalyticQConfidence.LOW})

    await issue_repo.add_issue(issue1)
    await issue_repo.add_issue(issue2)
    await issue_repo.add_issue(issue3)

    # Filter issues by severity and confidence
    filtered_issues = await issue_repo.filter_scan_issues(1, severity=AnalyticQSeverity.MEDIUM, confidence=AnalyticQConfidence.MEDIUM)
    assert len(filtered_issues) == 1
    assert filtered_issues[0].severity == AnalyticQSeverity.MEDIUM
    assert filtered_issues[0].confidence == AnalyticQConfidence.MEDIUM


@pytest.mark.asyncio
async def test_delete_issue_by_id(issue_repo):
    # Add an issue to the database
    issue = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)
    await issue_repo.add_issue(issue)

    # Delete the issue
    await issue_repo.delete_issue_by_id(1)

    # Verify the issue was deleted
    deleted_issue = await issue_repo.get_issue_by_id(1)
    assert deleted_issue is None
