from unittest.mock import AsyncMock

import pytest
from analyticq.engine import AnalyticQSASTScanResultModel
from analyticq.repository.scan_repository import AnalyticQScanResultRepository
from analyticq.schemas.scan_dto import ScanCreateRequest, ScanUpdateRequest
from analyticq.service import AnalyticQScanService
from fastapi import HTTPException, status


@pytest.fixture
def scan_repository():
    return AsyncMock(spec=AnalyticQScanResultRepository)


@pytest.fixture
def scan_service(scan_repository):
    return AnalyticQScanService(scan_repository)


# Test data
TEST_SCAN_DATA = {
    "scan_id": "scan_123",
    "context_id": 1,
    "tool_name": "tool_1",
    "summary": {"key": "value"},
    "scan_metadata": {"key": "value"},
    "issues": []
}

# Test data
TEST_UPDATED_DATA = {
    "scan_id": "scan_123",
    "context_id": 1,
    "tool_name": "tool_2",
    "summary": {"new_key": "new_value"},
    "scan_metadata": {"new_key": "new_value"},
    "issues": []
}

TEST_ISSUE_DATA = {
    "id": 1,
    "scan_id": "scan_123",
    "rule_id": "rule_456",
    "severity": "HIGH",
    "confidence": "HIGH",
    "code": "print('Hello, World!')",
    "message": "Potential security issue",
    "path": "/path/to/file.py",
    "start_line": 10,
    "end_line": 10,
    "column": 5,
    "issue_metadata": {"key": "value"},
    "summary": {"key": "value"}
}


@pytest.mark.asyncio
async def test_create_scan_success(scan_service, scan_repository):
    """
    Test creating a scan successfully.
    """
    # Mock the repository to return a valid scan
    scan_repository.add_scan.return_value = AnalyticQSASTScanResultModel(**TEST_SCAN_DATA)

    # Create a ScanCreateRequest object
    scan_data = ScanCreateRequest(**TEST_SCAN_DATA)

    # Call the service method
    result = await scan_service.create_scan(scan_data)

    # Assert the result
    assert isinstance(result, AnalyticQSASTScanResultModel)
    assert result.scan_id == "scan_123"
    scan_repository.add_scan.assert_called_once_with(scan_data)


@pytest.mark.asyncio
async def test_update_scan_failure(scan_service, scan_repository):
    """
    Test updating a scan with a failure.
    """
    # Mock the repository to raise an exception
    scan_repository.update_by_scan_id.side_effect = Exception("Database error")

    # Create a ScanUpdateRequest object
    updated_data = ScanUpdateRequest(summary={"new_key": "new_value"})

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await scan_service.update_scan("scan_123", updated_data)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error updating scan: Database error"
    scan_repository.update_by_scan_id.assert_called_once_with("scan_123", summary={"new_key": "new_value"})


@pytest.mark.asyncio
async def test_create_scan_failure(scan_service, scan_repository):
    """
    Test creating a scan with a failure.
    """
    # Mock the repository to raise an exception
    scan_repository.add_scan.side_effect = Exception("Database error")

    # Create a ScanCreateRequest object
    scan_data = ScanCreateRequest(**TEST_SCAN_DATA)

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await scan_service.create_scan(scan_data)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error creating scan Database error"
    scan_repository.add_scan.assert_called_once_with(scan_data)


@pytest.mark.asyncio
async def test_get_scan_success(scan_service, scan_repository):
    """
    Test retrieving a scan by its ID successfully.
    """
    # Mock the repository to return a valid scan
    scan_repository.get_by_scan_id.return_value = AnalyticQSASTScanResultModel(**TEST_SCAN_DATA)

    # Call the service method
    result = await scan_service.get_scan_by_id("scan_123")

    # Assert the result
    assert isinstance(result, AnalyticQSASTScanResultModel)
    assert result.scan_id == "scan_123"
    scan_repository.get_by_scan_id.assert_called_once_with("scan_123")


@pytest.mark.asyncio
async def test_delete_scan_success(scan_service, scan_repository):
    """
    Test deleting a scan successfully.
    """
    # Mock the repository to return None
    scan_repository.delete_scan_by_id.return_value = AnalyticQSASTScanResultModel(**TEST_SCAN_DATA)

    # Call the service method
    await scan_service.delete_scan("scan_123")

    # Assert the repository method was called
    scan_repository.delete_scan_by_id.assert_called_once_with("scan_123")


@pytest.mark.asyncio
async def test_delete_scan_failure(scan_service, scan_repository):
    """
    Test deleting a scan with a failure.
    """
    # Mock the repository to raise an exception
    scan_repository.delete_scan_by_id.side_effect = Exception("Database error")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await scan_service.delete_scan("scan_123")

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error deleting spam : Database error"
    scan_repository.delete_scan_by_id.assert_called_once_with("scan_123")
