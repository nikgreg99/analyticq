from unittest.mock import AsyncMock

import pytest
from analyticq.repository.stats_repository import (AnalyticQContextModel,
                                                   AnalyticQStatsModel,
                                                   AnalyticQStatsRepository)
from analyticq.service import AnalyticQStatsService
from analyticq.validator.context import AnalyticQCodebaseType
from fastapi import HTTPException, status


@pytest.fixture
def stats_repository():
    return AsyncMock(spec=AnalyticQStatsRepository)


@pytest.fixture
def stats_service(stats_repository):
    return AnalyticQStatsService(stats_repository)


# Test data
TEST_STATS_DATA = {
    "id": 1,
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

TEST_CONTEXT_DATA = {
    "id": 1,
    "repo_name": "test_repo",
    "input_type": AnalyticQCodebaseType.SCRIPT,
    "branch": "main",
    "last_commit_hash": "abc123"
}


@pytest.mark.asyncio
async def test_create_stats_success(stats_repository, stats_service):
    stats_repository.add_statistics.return_value = AnalyticQStatsModel(**TEST_STATS_DATA)

    # Create an AnalyticQStatsModel object
    stats_data = AnalyticQStatsModel(**TEST_STATS_DATA)

    result = await stats_service.create_stats(stats_data)

    assert isinstance(result, AnalyticQStatsModel)
    assert result.id == 1
    stats_repository.add_statistics.assert_called_once_with(stats_data)


@pytest.mark.asyncio
async def test_create_stats_validation_error(stats_service, stats_repository):

    stats_repository.add_statistics.side_effect = ValueError("Invalid data")
    stats_data = AnalyticQStatsModel(**TEST_STATS_DATA)

    with pytest.raises(HTTPException) as exc_info:
        await stats_service.create_stats(stats_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid input data: Invalid data" in exc_info.value.detail
    stats_repository.add_statistics.assert_called_once_with(stats_data)


@pytest.mark.asyncio
async def test_create_stats_unexpected_error(stats_service, stats_repository):
    """
    Test creating stats with unexpected error.
    """
    # Mock the repository to raise Exception
    stats_repository.add_statistics.side_effect = Exception("Database error")

    # Create an AnalyticQStatsModel object
    stats_data = AnalyticQStatsModel(**TEST_STATS_DATA)

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await stats_service.create_stats(stats_data)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in exc_info.value.detail
    stats_repository.add_statistics.assert_called_once_with(stats_data)


@pytest.mark.asyncio
async def test_get_stats_success(stats_service, stats_repository):
    stats_repository.get_stats_by_id.return_value = AnalyticQStatsModel(**TEST_STATS_DATA)

    result = await stats_service.get_stats(1)

    assert isinstance(result, AnalyticQStatsModel)
    assert result.id == 1
    stats_repository.get_stats_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_stats_not_found(stats_service, stats_repository):
    """
    Test retrieving stats that do not exist.
    """
    # Mock the repository to return None
    stats_repository.get_stats_by_id.return_value = None

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException):
        await stats_service.get_stats(1)

    # Assert the exception details
    stats_repository.get_stats_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_stats_unexpected_error(stats_service, stats_repository):
    """
    Test retrieving stats with unexpected error.
    """
    # Mock the repository to raise Exception
    stats_repository.get_stats_by_id.side_effect = Exception("Database error")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await stats_service.get_stats(1)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in exc_info.value.detail
    stats_repository.get_stats_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_context_by_stats_id_success(stats_service, stats_repository):

    stats_repository.get_context_by_id.return_value = AnalyticQContextModel(**TEST_CONTEXT_DATA)

    context = await stats_service.get_context_by_stats_id(1)

    assert isinstance(context, AnalyticQContextModel)
    assert context.stats_id == 1
    stats_repository.get_context_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_context_by_stats_id_not_found(stats_service, stats_repository):
    stats_repository.get_context_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await stats_service.get_context_by_stats_id(1)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    stats_repository.get_context_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_context_by_stats_id_unexpected_error(stats_service, stats_repository):
    """
    Test retrieving context with unexpected error.
    """
    # Mock the repository to raise Exception
    stats_repository.get_context_by_id.side_effect = Exception("Database error")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await stats_service.get_context_by_stats_id(1)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in exc_info.value.detail
    stats_repository.get_context_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_stats_success(stats_service, stats_repository):
    """
    Test deleting stats successfully.
    """
    # Mock the repository to return True
    stats_repository.delete_stats.return_value = True

    # Call the service method
    await stats_service.delete_stats(1)

    # Assert the repository method was called
    stats_repository.delete_stats.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_stats_not_found(stats_service, stats_repository):
    """
    Test deleting stats that do not exist.
    """
    # Mock the repository to return False
    stats_repository.delete_stats.return_value = False

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await stats_service.delete_stats(1)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Stats with 1 not found" in exc_info.value.detail
    stats_repository.delete_stats.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_stats_unexpected_error(stats_service, stats_repository):
    """
    Test deleting stats with unexpected error.
    """
    # Mock the repository to raise Exception
    stats_repository.delete_stats.side_effect = Exception("Database error")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await stats_service.delete_stats(1)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error deleting stats Database error" in exc_info.value.detail
    stats_repository.delete_stats.assert_called_once_with(1)
