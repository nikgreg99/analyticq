import os
from pathlib import Path

import pytest
from analyticq.config import AnalyticQBaseConfig, AnalyticQEnvironmentLoader
from analyticq.manager.db_manager import AnalyticQDatabaseManager
from analyticq.repository.context_repository import (
    AnalyticQContextModel, AnalyticQContextRepository)
from analyticq.repository.scan_repository import (
    AnalyticQSASTScanResultModel, AnalyticQScanResultRepository)
from analyticq.repository.stats_repository import \
    AnalyticQStatsRepository  # noqa

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent


@pytest.fixture
def scan_repo():
    return AnalyticQScanResultRepository()


@pytest.fixture
def context_repo():
    return AnalyticQContextRepository()


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
    yield
    await db_manager.close()


@pytest.mark.asyncio
async def test_add_scan_context(context_repo, setup_db):
    """
    Test adding a new scan context and retrieving it.
    """
    scan_context = AnalyticQContextModel(
        repo_name="test-repo",
        branch="main",
        last_commit_hash="abc123"
    )

    await context_repo.add(scan_context)

    # Retrieve the scan context
    retrieved_context = await context_repo.get_by_repo_name("test-repo")
    assert retrieved_context is not None
    assert retrieved_context.repo_name == "test-repo"
    assert retrieved_context.branch == "main"
    assert retrieved_context.last_commit_hash == "abc123"


@pytest.mark.asyncio
async def test_get_by_id(context_repo, setup_db):
    """
    Test retrieving a scan context by ID.
    """
    # First, add a scan context
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-2",
        branch=None,
        last_commit_hash=None
    )
    await context_repo.add(scan_context)

    # Get the scan context by repo name first to get its ID
    context_by_repo = await context_repo.get_by_repo_name("test-repo-2")
    assert context_by_repo is not None

    # Now get it by ID
    context_by_id = await context_repo.get_by_id(context_by_repo.id)
    assert context_by_id is not None
    assert context_by_id.repo_name == "test-repo-2"


@pytest.mark.asyncio
async def test_update_scan_context(context_repo, setup_db):
    """Test updating a scan context."""
    # Create and add a test scan context
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-3",
        branch="develop",
        last_commit_hash="def456"
    )
    await context_repo.add(scan_context)

    # Update the scan context
    await context_repo.update_by_repo_name(
        "test-repo-3",
        branch="feature-branch",
        last_commit_hash="ghi789"
    )

    # Retrieve and verify updates
    updated_context = await context_repo.get_by_repo_name("test-repo-3")

    assert updated_context is not None
    assert updated_context.branch == "feature-branch"
    assert updated_context.last_commit_hash == "ghi789"
    # Input type should remain unchanged


@pytest.mark.asyncio
async def test_delete_scan_context(context_repo, setup_db):
    """Test deleting a scan context."""
    # Create and add a test scan context
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-4",
    )
    await context_repo.add(scan_context)

    # Verify it exists
    assert await context_repo.get_by_repo_name("test-repo-4") is not None

    # Delete it
    await context_repo.delete_by_repo_name("test-repo-4")

    # Verify it's gone
    assert await context_repo.get_by_repo_name("test-repo-4") is None


@pytest.mark.asyncio
async def test_scan_context_with_null_values(context_repo, setup_db):
    """Test adding a scan context with null values for optional fields."""
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-5",
        # branch and last_commit_hash are omitted
    )
    await context_repo.add(scan_context)

    # Retrieve the scan context
    retrieved_context = await context_repo.get_by_repo_name("test-repo-5")
    assert retrieved_context is not None
    assert retrieved_context.repo_name == "test-repo-5"
    assert retrieved_context.branch is None
    assert retrieved_context.last_commit_hash is None


@pytest.mark.asyncio
async def test_get_scans_by_repo_name(context_repo, scan_repo, setup_db):
    # Add a context
    scan_context = AnalyticQContextModel(
        id="1",
        repo_name="test_repo",
        branch=None,
        last_commit_hash=None
    )

    await context_repo.add(scan_context)

    scan_1 = AnalyticQSASTScanResultModel(
        scan_id="1",
        context_id=scan_context.id,
        scan_metadata={"tool_name": "njsscan"}
    )

    scan_2 = AnalyticQSASTScanResultModel(
        scan_id="2",
        context_id=scan_context.id,
        scan_metadata={"tool_name": "njsscan"}
    )

    await scan_repo.add(scan_1)
    await scan_repo.add(scan_2)

    scans = await context_repo.get_scans_by_repo_name("test_repo")
    assert len(scans) == 2
    assert isinstance(scans[0], AnalyticQSASTScanResultModel)
    assert scans[0].scan_id == "1"
    assert scans[1].scan_id == "2"


@pytest.mark.asyncio
async def test_get_scans_by_repo_non_existing(context_repo):
    scans = await context_repo.get_scans_by_repo_name("nonexistent_repo")
    assert len(scans) == 0


@pytest.mark.asyncio
async def test_get_scans_by_repo_name_no_scans(context_repo):
    context = AnalyticQContextModel(
        repo_name="test_repo",
        branch=None,
        last_commit_hash=None
    )
    await context_repo.add(context)

    scans = await context_repo.get_scans_by_repo_name("test_repo")
    assert len(scans) == 0
