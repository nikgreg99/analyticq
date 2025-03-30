from unittest.mock import AsyncMock

import pytest
from analyticq.engine import (AnalyticQConfidence, AnalyticQSASTIssueModel,
                              AnalyticQSeverity)
from analyticq.repository.issue_repository import AnalyticQSASTIssueRepository
from analyticq.schemas.issue_dto import IssueCreateRequest, IssueUpdateRequest
from analyticq.service import AnalyticQSASTIssueService
from fastapi import HTTPException, status


@pytest.fixture
def issue_repository():
    return AsyncMock(spec=AnalyticQSASTIssueRepository)


@pytest.fixture
def issue_service(issue_repository):
    return AnalyticQSASTIssueService(issue_repository)


# Test data
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
async def test_get_issue_success(issue_service, issue_repository):
    """
    Test retrieving an issue by its ID successfully.
    """
    # Mock the repository to return a valid issue
    issue_repository.get_by_id.return_value = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)

    # Call the service method
    result = await issue_service.get_issue(1)

    # Assert the result
    assert isinstance(result, AnalyticQSASTIssueModel)
    assert result.id == 1
    issue_repository.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_issue_not_found(issue_service, issue_repository):
    """
    Test retrieving an issue that does not exist.
    """
    # Mock the repository to return None
    issue_repository.get_by_id.return_value = None

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await issue_service.get_issue(1)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    issue_repository.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_issue_success(issue_service, issue_repository):
    """
    Test creating an issue successfully.
    """
    # Mock the repository to return a valid issue
    issue_repository.add.return_value = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)

    # Create an IssueCreateRequest object
    issue_data = IssueCreateRequest(**TEST_ISSUE_DATA)

    # Call the service method
    result = await issue_service.create_issue(issue_data)

    # Assert the result
    assert isinstance(result, AnalyticQSASTIssueModel)
    assert result.id == 1
    issue_repository.add.assert_called_once_with(issue_data)


@pytest.mark.asyncio
async def test_update_issue_success(issue_service, issue_repository):
    """
    Test updating an issue successfully.
    """
    # Mock the repository to return a valid issue
    issue_repository.update_by_id.return_value = AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)

    # Create an IssueUpdateRequest object
    updated_data = IssueUpdateRequest(severity="HIGH")

    # Call the service method
    result = await issue_service.update_issue(1, updated_data)

    # Assert the result
    assert isinstance(result, AnalyticQSASTIssueModel)
    assert result.severity == AnalyticQSeverity.HIGH
    issue_repository.update_by_id.assert_called_once_with(1, severity=AnalyticQSeverity.HIGH)


@pytest.mark.asyncio
async def test_delete_issue_success(issue_service, issue_repository):
    """
    Test deleting an issue successfully.
    """
    # Mock the repository to return None
    issue_repository.delete_by_id.return_value = None

    # Call the service method
    await issue_service.delete_issue(1)

    # Assert the repository method was called
    issue_repository.delete_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_filter_scan_issues_success(issue_service, issue_repository):
    """
    Test filtering scan issues successfully.
    """
    # Mock the repository to return a list of issues
    issue_repository.filter_scan_issues.return_value = [
        AnalyticQSASTIssueModel(**TEST_ISSUE_DATA)
    ]

    # Call the service method
    result = await issue_service.filter_scan_issues("scan_123", severity="HIGH", confidence="HIGH")

    # Assert the result
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], AnalyticQSASTIssueModel)
    issue_repository.filter_scan_issues.assert_called_once_with("scan_123", "HIGH", "HIGH")


@pytest.mark.asyncio
async def test_filter_scan_issues_failure(issue_service, issue_repository):
    """
    Test filtering scan issues with a failure.
    """
    # Mock the repository to raise an exception
    issue_repository.filter_scan_issues.side_effect = Exception("Database error")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await issue_service.filter_scan_issues("scan_123", AnalyticQSeverity.HIGH, AnalyticQConfidence.HIGH)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error retrieving issues Database error"
    issue_repository.filter_scan_issues.assert_called_once_with("scan_123", AnalyticQSeverity.HIGH, AnalyticQConfidence.HIGH)


@pytest.mark.asyncio
async def test_delete_issue_failure(issue_service, issue_repository):
    """
    Test deleting an issue with a failure.
    """
    # Mock the repository to raise an exception
    issue_repository.delete_by_id.side_effect = Exception("Database error")

    # Call the service method and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await issue_service.delete_issue(1)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error deleting issue: Database error"
    issue_repository.delete_by_id.assert_called_once_with(1)
