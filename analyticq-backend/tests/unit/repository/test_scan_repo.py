import os
from pathlib import Path

import pytest
from analyticq.config import AnalyticQBaseConfig, AnalyticQEnvironmentLoader
from analyticq.manager.db_manager import AnalyticQDatabaseManager
from analyticq.repository.context_repository import \
    AnalyticQContextRepository  # noqa
from analyticq.repository.scan_repository import (  # noqa
    AnalyticQSASTScanResult, AnalyticQSASTScanResultModel,
    AnalyticQScanResultRepository)
from analyticq.repository.stats_repository import \
    AnalyticQStatsRepository  # noqa
from analyticq.validator.issue import AnalyticQConfidence, AnalyticQSeverity
from sqlalchemy import select, text

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent


@pytest.fixture
def scan_repo():
    return AnalyticQScanResultRepository()


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
        await session.execute(text("DELETE FROM analyticq_sast_scan_results"))
        await session.commit()

    await db_manager.close()


# Test data
TEST_SCAN_RESULT_DATA = {
    "id": 1,
    "scan_id": "scan_123",
    "tool_name": "Bandit",
    "issues": [],
    "summary": {"key": "value"},
    "scan_metadata": {"key": "value"},
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
}

# Test data
TEST_UPDATED_RESULT_DATA = {
    "id": 1,
    "scan_id": "scan_123",
    "tool_name": "Bandit",
    "issues": [],
    "summary": {"new_key": "new_value"},
    "scan_metadata": {"key": "value"},
    "created_at": "2023-10-01T12:00:00Z",
    "updated_at": "2023-10-01T12:00:00Z"
}

TEST_ISSUE_DATA = {
    "scan_id": 1,
    "rule_id": "rule_456",
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


@pytest.mark.asyncio
async def test_add_scan_result(scan_repo):
    # Create a scan result model
    scan_result = AnalyticQSASTScanResultModel(**TEST_SCAN_RESULT_DATA)

    # Add the scan result to the database
    await scan_repo.add_scan(scan_result)

    # Verify the scan result was added
    async with AnalyticQDatabaseManager().get_db_session() as session:
        result = await session.execute(
            select(AnalyticQSASTScanResult)
            .where(AnalyticQSASTScanResult.scan_id == "scan_123")
        )

        scan_results = result.scalars().unique().all()
        assert len(scan_results) == 1
        assert scan_results[0].scan_id == "scan_123"


@pytest.mark.asyncio
async def test_get_scan_result_by_scan_id(scan_repo):
    # Add a scan result to the database
    scan_result = AnalyticQSASTScanResultModel(**TEST_SCAN_RESULT_DATA)
    await scan_repo.add_scan(scan_result)

    # Retrieve the scan result by scan_id
    retrieved_scan_result = await scan_repo.get_by_scan_id(1)
    assert retrieved_scan_result is not None
    assert retrieved_scan_result.id == 1


@pytest.mark.asyncio
async def test_update_scan_result_by_scan_id(scan_repo):
    # Add a scan result to the database
    scan_result = AnalyticQSASTScanResultModel(**TEST_SCAN_RESULT_DATA)
    updated_scan_result = AnalyticQSASTScanResultModel(**TEST_UPDATED_RESULT_DATA)
    await scan_repo.add_scan(scan_result)

    # Update the scan result
    await scan_repo.update_scan_by_id(scan_result.id, updated_scan_result)

    # Verify the update
    updated_scan_result = await scan_repo.get_by_scan_id(scan_result.id)
    assert updated_scan_result.summary == {"new_key": "new_value"}


@pytest.mark.asyncio
async def test_delete_scan_result_by_scan_id(scan_repo):
    # Add a scan result to the database
    scan_result = AnalyticQSASTScanResultModel(**TEST_SCAN_RESULT_DATA)
    await scan_repo.add_scan(scan_result)

    # Delete the scan result
    await scan_repo.delete_scan_by_id(scan_result.id)

    # Verify the scan result was deleted
    deleted_scan_result = await scan_repo.get_by_scan_id(scan_result.id)
    assert deleted_scan_result is None
