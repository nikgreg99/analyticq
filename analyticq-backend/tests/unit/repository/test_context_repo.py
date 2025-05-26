import datetime
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
    async with db_manager.get_db_session() as session:

        await session.commit()

    yield
    await db_manager.close()


@pytest.mark.asyncio
async def test_get_all_contexts_empty(context_repo, setup_db):

    all_contexts = await context_repo.get_all_contexts()

    assert isinstance(all_contexts, list)


@pytest.mark.asyncio
async def test_get_contexts_paginated(context_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    contexts = [
        AnalyticQContextModel(repo_name=f"test-repo-paginated-{i}",
                              branch=f"branch-{i}",
                              last_commit_hash=f"hash-{i}",
                              created_at=now,
                              updated_at=now)
        for i in range(15)
    ]

    for context in contexts:
        await context_repo.add(context)

    page_1_contexts, total_count = await context_repo.get_contexts_paginated(1, 5)

    assert len(page_1_contexts) == 5
    assert total_count >= 1

    page_2_contexts, _ = await context_repo.get_contexts_paginated(2, 5)

    assert len(page_2_contexts) == 5

    page_1_repo_names = [context.repo_name for context in page_1_contexts]
    page_2_repo_names = [context.repo_name for context in page_2_contexts]

    # No context should appear on both pages
    assert not any(name in page_2_repo_names for name in page_1_repo_names)


@pytest.mark.asyncio
async def test_get_contexts_paginated_out_of_range(context_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    contexts = [
        AnalyticQContextModel(repo_name=f"test-repo-pagination-{i}",
                              created_at=now, updated_at=now)
        for i in range(3)
    ]

    for context in contexts:
        await context_repo.add(context)

    far_page_contexts, total_count = await context_repo.get_contexts_paginated(10, 5)

    assert len(far_page_contexts) == 0  # Should be empty
    assert total_count >= 3  # Should still report total count correctly


@pytest.mark.asyncio
async def test_get_contexts_paginated_edge_cases(context_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    # Create and add a few test contexts
    contexts = [
        AnalyticQContextModel(repo_name=f"test-repo-edge-{i}",
                              created_at=now, updated_at=now)
        for i in range(5)
    ]

    for context in contexts:
        await context_repo.add(context)

    # Test with page_size larger than total items
    large_page_contexts, total_count = await context_repo.get_contexts_paginated(1, 20)
    assert len(large_page_contexts) >= 5  # Should return all available contexts
    assert total_count >= 5

    # Test with page = 0 (invali)
    with pytest.raises(ValueError):
        await context_repo.get_contexts_paginated(0, 5)

    # Test woth negative page size
    with pytest.raises(ValueError):
        await context_repo.get_contexts_paginated(1, -5)


@pytest.mark.asyncio
async def test_add_context(context_repo):
    """
    Test adding a new scan context and retrieving it.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    scan_context = AnalyticQContextModel(
        repo_name="test-repo",
        branch="main",
        last_commit_hash="abc123",
        created_at=now,
        updated_at=now
    )

    await context_repo.add(scan_context)

    # Retrieve the scan context
    retrieved_context = await context_repo.get_by_repo_name("test-repo")
    assert retrieved_context is not None
    assert retrieved_context.repo_name == "test-repo"
    assert retrieved_context.branch == "main"
    assert retrieved_context.last_commit_hash == "abc123"


@pytest.mark.asyncio
async def test_add_context_if_not_found(context_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-unique",
        branch="main",
        last_commit_hash="abc123",
        created_at=now,
        updated_at=now
    )

    added_context = await context_repo.add_if_not_exists(scan_context)
    assert added_context is not None
    assert added_context.repo_name == "test-repo-unique"
    assert added_context.branch == "main"


@pytest.mark.asyncio
async def test_get_by_id(context_repo):
    """
    Test retrieving a scan context by ID.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    # First, add a scan context
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-2",
        branch="main",
        last_commit_hash="abc123",
        created_at=now,
        updated_at=now
    )
    await context_repo.add(scan_context)

    # Get the scan context by repo name first to get its ID
    context_by_repo = await context_repo.get_by_repo_name("test-repo-2")
    assert context_by_repo is not None

    new_context = AnalyticQContextModel(
        repo_name="test-repo-unique",
        branch="main",
        last_commit_hash="def456",
        created_at=now,
        updated_at=now
    )

    # Now get it by ID
    context_by_id = await context_repo.get_by_id(context_by_repo.id)
    assert context_by_id is not None
    assert context_by_id.repo_name == "test-repo-2"

    returned_context = await context_repo.add_if_not_exists(new_context)
    assert returned_context is not None
    assert returned_context.repo_name == "test-repo-unique"
    # Should still have the original values, not the new ones
    assert returned_context.branch == "main"
    assert returned_context.last_commit_hash == "def456"

    all_contexts = await context_repo.get_all_contexts()
    matching_context = [context for context in all_contexts if context.repo_name == "test-repo-unique"]
    assert len(matching_context) == 1


@pytest.mark.asyncio
async def test_update_scan_context(context_repo):
    """Test updating a scan context."""
    now = datetime.datetime.now(datetime.timezone.utc)
    # Create and add a test scan context
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-3",
        branch="develop",
        last_commit_hash="def456",
        created_at=now,
        updated_at=now
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
async def test_delete_scan_context(context_repo):
    """Test deleting a scan context."""
    now = datetime.datetime.now(datetime.timezone.utc)
    # Create and add a test scan context
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-4",
        created_at=now,
        updated_at=now
    )
    await context_repo.add(scan_context)

    # Verify it exists
    assert await context_repo.get_by_repo_name("test-repo-4") is not None

    # Delete it
    await context_repo.delete_by_repo_name("test-repo-4")

    # Verify it's gone
    assert await context_repo.get_by_repo_name("test-repo-4") is None


@pytest.mark.asyncio
async def test_scan_context_with_null_values(context_repo):
    """Test adding a scan context with null values for optional fields."""
    now = datetime.datetime.now(datetime.timezone.utc)
    scan_context = AnalyticQContextModel(
        repo_name="test-repo-5",
        # branch and last_commit_hash are omitted
        created_at=now,
        updated_at=now
    )
    await context_repo.add(scan_context)

    # Retrieve the scan context
    retrieved_context = await context_repo.get_by_repo_name("test-repo-5")
    assert retrieved_context is not None
    assert retrieved_context.repo_name == "test-repo-5"
    assert retrieved_context.branch is None
    assert retrieved_context.last_commit_hash is None


@pytest.mark.asyncio
async def test_get_scans_by_repo_name(context_repo, scan_repo):
    now = datetime.datetime.now(datetime.timezone.utc)
    # Add a context
    scan_context = AnalyticQContextModel(
        id="1",
        repo_name="test_repo",
        branch=None,
        last_commit_hash=None,
        created_at=now,
        updated_at=now
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

    await scan_repo.add_scan(scan_1)
    await scan_repo.add_scan(scan_2)

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
    now = datetime.datetime.now(datetime.timezone.utc)
    context = AnalyticQContextModel(
        repo_name="test_repo",
        branch=None,
        last_commit_hash=None,
        created_at=now,
        updated_at=now
    )
    await context_repo.add(context)

    scans = await context_repo.get_scans_by_repo_name("test_repo")
    assert len(scans) == 0
