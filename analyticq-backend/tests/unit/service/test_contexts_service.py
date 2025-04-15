from unittest.mock import AsyncMock

import pytest
from analyticq.repository.context_repository import AnalyticQContextRepository
from analyticq.repository.scan_repository import AnalyticQSASTScanResultModel
from analyticq.schemas.context_dto import (AnalyticQCodebaseType,
                                           ContextCreateRequest,
                                           ContextUpdateRequest)
from analyticq.service.context_service import (AnalyticQContextModel,
                                               AnalyticQContextService)
from fastapi import HTTPException, status


@pytest.fixture
def context_repository():
    return AsyncMock(spec=AnalyticQContextRepository)


@pytest.fixture
def context_service(context_repository: AsyncMock):
    return AnalyticQContextService(context_repository)


# Test data
TEST_CONTEXT_DATA = {
    "repo_name": "test_repo",
    "input_type": AnalyticQCodebaseType.SCRIPT,
    "branch": "main",
    "last_commit_hash": "abc123"
}

TEST_SCAN_DATA = {
    "scan_id": "scan_123",
    "context_id": 1,
    "tool_name": "tool_1",
    "summary": {"key": "value"},
    "scan_metadata": {"key": "value"}
}


@pytest.mark.asyncio
async def test_create_context_success(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test creating a context successfully.
    """
    # Mock the repository to return a valid context
    context_repository.add.return_value = AnalyticQContextModel(**TEST_CONTEXT_DATA)

    # Create a ContextCreateRequest object
    context_data = ContextCreateRequest(**TEST_CONTEXT_DATA)

    # Call the service method
    result = await context_service.create_context(context_data)

    # Assert the result
    assert isinstance(result, AnalyticQContextModel)
    assert result.repo_name == "test_repo"
    context_repository.add.assert_called_once_with(context_data)


@pytest.mark.asyncio
async def test_create_context_failure(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test creating a context with a failure.
    """
    # Mock the repository to raise an exception
    context_repository.add.side_effect = Exception("Database error")

    # Create a ContextCreateRequest object
    context_data = ContextCreateRequest(**TEST_CONTEXT_DATA)

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await context_service.create_context(context_data)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "An error occurred while creating the context: Database error"
    context_repository.add.assert_called_once_with(context_data)


@pytest.mark.asyncio
async def test_get_context_by_repo_name_success(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test retrieving a context by its repository name successfully.
    """
    # Mock the repository to return a valid context
    context_repository.get_by_repo_name.return_value = TEST_CONTEXT_DATA

    # Call the service method
    result = await context_service.get_context_by_repo_name("test_repo")

    # Assert the result
    assert result == TEST_CONTEXT_DATA
    context_repository.get_by_repo_name.assert_called_once_with("test_repo")


@pytest.mark.asyncio
async def test_get_context_by_repo_name_not_found(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test retrieving a context that does not exist.
    """
    # Mock the repository to return None
    context_repository.get_by_repo_name.return_value = None

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await context_service.get_context_by_repo_name("test_repo")

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    context_repository.get_by_repo_name.assert_called_once_with("test_repo")


@pytest.mark.asyncio
async def test_get_scans_by_repo_name_success(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test retrieving scans by repository name successfully.
    """
    # Mock the repository to return a list of scans
    context_repository.get_scans_by_repo_name.return_value = [AnalyticQSASTScanResultModel(**TEST_SCAN_DATA)]

    # Call the service method
    result = await context_service.get_scans_by_repo_name("test_repo")

    # Assert the result
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], AnalyticQSASTScanResultModel)
    context_repository.get_scans_by_repo_name.assert_called_once_with("test_repo")


@pytest.mark.asyncio
async def test_get_scans_by_repo_name_not_found(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test retrieving scans for a repository that does not exist.
    """
    # Mock the repository to return an empty list
    context_repository.get_scans_by_repo_name.return_value = []

    scans = await context_service.get_scans_by_repo_name("test_repo")

    # Assert the exception details
    assert isinstance(scans, list)
    assert len(scans) == 0
    context_repository.get_scans_by_repo_name.assert_called_once_with("test_repo")


@pytest.mark.asyncio
async def test_update_context_failure(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test updating a context with a failure.
    """
    # Mock the repository to raise an exception
    context_repository.update_by_repo_name.side_effect = Exception("Database error")

    # Create a ContextUpdateRequest object
    update_data = ContextUpdateRequest(branch="feature-branch")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await context_service.update_context("test_repo", update_data)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    context_repository.update_by_repo_name.assert_called_once_with("test_repo", branch="feature-branch")


@pytest.mark.asyncio
async def test_delete_context_success(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test deleting a context successfully.
    """
    # Mock the repository to return None
    context_repository.delete_by_repo_name.return_value = None

    # Call the service method
    await context_service.delete_context("test_repo")

    # Assert the repository method was called
    context_repository.delete_by_repo_name.assert_called_once_with("test_repo")


@pytest.mark.asyncio
async def test_delete_context_failure(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test deleting a context with a failure.
    """
    # Mock the repository to raise an exception
    context_repository.delete_by_repo_name.side_effect = Exception("Database error")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await context_service.delete_context("test_repo")

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "An error occurred while deleting the context."
    context_repository.delete_by_repo_name.assert_called_once_with("test_repo")


@pytest.mark.asyncio
async def test_create_context_if_not_exists_success(context_service: AnalyticQContextService, context_repository: AsyncMock):
    """
    Test creating a context if it doesn't exist successfully.
    """
    # Mock the repository to return a valid context
    context_repository.add_if_not_exists.return_value = AnalyticQContextModel(**TEST_CONTEXT_DATA)

    # Create a ContextCreateRequest object
    context_data = ContextCreateRequest(**TEST_CONTEXT_DATA)

    # Call the service method
    result = await context_service.create_context_if_not_exists(context_data)

    # Assert the result
    assert isinstance(result, AnalyticQContextModel)
    assert result.repo_name == "test_repo"
    context_repository.add_if_not_exists.assert_called_once_with(context_data)


@pytest.mark.asyncio
async def test_create_context_if_not_exists_validation_error(context_service, context_repository):

    context_repository.add_if_not_exists.side_effect = ValueError("Invalid input data")

    context_data = ContextCreateRequest(**TEST_CONTEXT_DATA)

    with pytest.raises(HTTPException) as exc_info:
        await context_service.create_context_if_not_exists(context_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid input data" in exc_info.value.detail
    context_repository.add_if_not_exists.assert_called_once_with(context_data)


@pytest.mark.asyncio
async def test_create_context_if_not_exist_failure(context_service: AnalyticQContextService, context_repository: AsyncMock):
    context_repository.add_if_not_exists.side_effect = Exception("Database Error")

    context_data = ContextCreateRequest(**TEST_CONTEXT_DATA)

    with pytest.raises(HTTPException) as exc_info:
        await context_service.create_context_if_not_exists(context_data)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An error occurred while creating the context: Database Error" in exc_info.value.detail
    context_repository.add_if_not_exists.assert_called_once_with(context_data)
