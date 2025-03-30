import logging

from analyticq.repository.issue_repository import (
    AnalyticQSASTIssueModel, AnalyticQSASTIssueRepository)
from analyticq.schemas.issue_dto import IssueUpdateRequest
from analyticq.service import AnalyticQSASTIssueService
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

issue_router = APIRouter(prefix="/issues", tags=["Issue Management"])


class ErrorResponse(BaseModel):
    detail: str


def get_issue_service(
    repo: AnalyticQSASTIssueRepository = Depends(AnalyticQSASTIssueRepository)
) -> AnalyticQSASTIssueService:
    """Dependency provider for issue service."""
    return AnalyticQSASTIssueService(repo)


@issue_router.get(
    "/{issue_id}",
    response_model=AnalyticQSASTIssueModel,
    summary="Get issue by ID",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def get_issue(issue_id: int, service: AnalyticQSASTIssueService = Depends(get_issue_service)):
    """
    Retrieve a specific SAST issue by its ID.
    """
    return await service.get_issue(issue_id)


@issue_router.put(
    "/{issue_id}",
    response_model=AnalyticQSASTIssueModel,
    summary="Update issue by ID",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def update_issue(
    issue_id: int,
    update_data: IssueUpdateRequest,
    service: AnalyticQSASTIssueService = Depends(get_issue_service),
):
    """
    Update an existing issue with the provided data.
    """
    return await service.update_issue(issue_id, update_data)


@issue_router.delete(
    "/{issue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete issue by ID",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Issue successfully deleted"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def delete_issue(issue_id: int, service: AnalyticQSASTIssueService = Depends(get_issue_service)):
    """
    Delete an issue from the database by its ID.
    """
    await service.delete_issue(issue_id)
