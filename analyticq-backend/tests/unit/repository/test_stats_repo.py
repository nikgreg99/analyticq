import os
from pathlib import Path

import pytest
from analyticq.config import AnalyticQBaseConfig, AnalyticQEnvironmentLoader
from analyticq.manager.db_manager import AnalyticQDatabaseManager
from analyticq.repository.context_repository import \
    AnalyticQContextRepository  # noqa
from analyticq.repository.stats_repository import (AnalyticQStats,
                                                   AnalyticQStatsModel,
                                                   AnalyticQStatsRepository)
from sqlalchemy import select, text

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent


@pytest.fixture
def stats_repo():
    return AnalyticQStatsRepository()


@pytest.fixture(autouse=True)
async def setup_db():
    """Set up the database schema before each test and tear it down afterward."""
    test_file = BASE_DIR / "unit" / "test_files"
    AnalyticQBaseConfig.load_config_file(str(test_file), "test_config.json")

    test_env_file = BASE_DIR / "unit" / "test_files" / ".env.test"
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
        await session.execute(text("DELETE FROM analyticq_stats"))
        await session.commit()

    await db_manager.close()


TEST_STATS_DATA = {
    "files": {
        "Python": [
            {
                "file_path": "/path/to/file1.py",
                "loc": 100,
                "size": 5000
            },
            {
                "file_path": "/path/to/file2.py",
                "loc": 50,
                "size": 2500
            }
        ],
        "Markdown": [
            {
                "file_path": "/path/to/README.md",
                "loc": 30,
                "size": 1500
            }
        ]
    },
    "language_statistics": {
        "Python": {
            "file_count": 2,
            "total_size": 7500,
            "largest_file": {
                "path": "/path/to/file1.py",
                "size": 5000
            },
            "smallest_file": {
                "path": "/path/to/file2.py",
                "size": 2500
            },
            "average_size": 3750.0,
            "median_size": 3750,
            "std_size": 1250.0,
            "percentage_files": 66.67
        },
        "Markdown": {
            "file_count": 1,
            "total_size": 1500,
            "largest_file": {
                "path": "/path/to/README.md",
                "size": 1500
            },
            "smallest_file": {
                "path": "/path/to/README.md",
                "size": 1500
            },
            "average_size": 1500.0,
            "median_size": 1500,
            "std_size": 0,
            "percentage_files": 33.33
        }
    },
    "total_files_scanned": 3,
    "total_size_scanned": 9000,
    "excluded_directories": ["/path/to/excluded"],
    "excluded_files": {
        "id": 1,
        "count": 1,
        "total_size": 1000,
        "files": ["/path/to/excluded/file.txt"]
    }
}


@pytest.mark.asyncio
async def test_add_statistics(stats_repo):
    """Test adding statistics to the database."""
    stats = AnalyticQStatsModel(**TEST_STATS_DATA)
    added_stats = await stats_repo.add_stats(stats)
    assert added_stats is not None
    assert added_stats.id == 1


@pytest.mark.asyncio
async def test_get_stats_by_id(stats_repo):
    """Test retrieving statistics by ID."""
    # First add a record
    stats = AnalyticQStatsModel(**TEST_STATS_DATA)
    added_stats = await stats_repo.add_stats(stats)

    # Then retrieve it
    retrieved_stats = await stats_repo.get_stats_by_id(added_stats.id)

    assert retrieved_stats is not None
    assert retrieved_stats.id == added_stats.id
    assert retrieved_stats.total_size_scanned == 9000


@pytest.mark.asyncio
async def test_get_stats_by_id_not_found(stats_repo):
    """Test retrieving non-existent statistics returns None."""
    retrieved_stats = await stats_repo.get_stats_by_id(999)
    assert retrieved_stats is None


@pytest.mark.asyncio
async def test_delete_stats(stats_repo):
    """Test deleting statistics."""
    # First add a record
    stats = AnalyticQStatsModel(**TEST_STATS_DATA)
    added_stats = await stats_repo.add_stats(stats)

    # Then delete it
    deleted = await stats_repo.delete_stats(added_stats.id)
    assert deleted is True

    # Verify deletion
    async with AnalyticQDatabaseManager().get_db_session() as session:
        result = await session.execute(select(AnalyticQStats))
        records = result.scalars().all()
        assert len(records) == 0


@pytest.mark.asyncio
async def test_update_stats_success(stats_repo):
    original_stats = AnalyticQStatsModel(**TEST_STATS_DATA)
    added_stats = await stats_repo.add_stats(original_stats)

    updated_stats_data = AnalyticQStatsModel(
        **{
            **TEST_STATS_DATA,  # Copy original data
            "total_files_scanned": 5,  # Modify some fields
            "total_size_scanned": 15000,
            "excluded_directories": ["/path/to/excluded", "/another/path"]
        }
    )

    updated_stats = await stats_repo.update_stats(added_stats.id, updated_stats_data)

    assert updated_stats is not None
    assert updated_stats.id == added_stats.id
    assert updated_stats.total_files_scanned == 5
    assert updated_stats.total_size_scanned == 15000
    assert updated_stats.excluded_directories == ["/path/to/excluded", "/another/path"]


@pytest.mark.asyncio
async def test_update_stats_not_found(stats_repo):
    """Test updating non-existent statistics raises an exception."""
    # Prepare updated stats data
    updated_stats_data = AnalyticQStatsModel(**TEST_STATS_DATA)

    # Attempt to update a non-existent record
    with pytest.raises(Exception):  # Specifically, SQLAlchemy's NoResultFound
        await stats_repo.update_stats(999, updated_stats_data)


@pytest.mark.asyncio
async def test_delete_stats_not_found(stats_repo):
    """Test deleting non-existent statistics returns False."""
    deleted = await stats_repo.delete_stats(999)
    assert deleted is False
