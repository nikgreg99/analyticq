import logging
from typing import List, Optional

from analyticq.repository.context_repository import (
    AnalyticQContextModel, AnalyticQContextRepository,
    AnalyticQSASTScanResultModel)
from analyticq.schemas.context_dto import PaginatedContextResponse
from analyticq.service.context_service import AnalyticQContextService
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

context_router = APIRouter(prefix="/contexts", tags=["Context Management"])


class ErrorResponse(BaseModel):
    detail: str


def get_context_service(
    repo: AnalyticQContextRepository = Depends(AnalyticQContextRepository)
) -> AnalyticQContextService:
    """Dependency provider for context service."""
    return AnalyticQContextService(repo)


@context_router.get(
    "/",
    response_model=PaginatedContextResponse,
    summary="Get all contexts with optional pagination",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_all_contexts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Number of items per page, set to 0 for all items"),
    service: AnalyticQContextService = Depends(get_context_service)
):
    """
    Retrieve all security contexts with optional pagination.

    - **page**: Page number (starting from 1)
    - **page_size**: Number of items per page (set to 0 to get all items without pagination)
    - **returns**: Paginated list of contexts or all contexts if pagination is disabled
    """
    # Add a method to your service to handle this request
    if page_size == 0:
        # Get all contexts without pagination
        contexts = await service.get_all_contexts()
        return {
            "items": contexts,
            "total": len(contexts),
            "page": 1,
            "page_size": len(contexts),
            "has_more": False
        }
    else:
        # Get contexts with pagination
        contexts, total = await service.get_contexts_paginated(page, page_size)
        return {
            "items": contexts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < total
        }


def get_context_service(
    repo: AnalyticQContextRepository = Depends(AnalyticQContextRepository)
) -> AnalyticQContextService:
    """Dependency provider for context service."""
    return AnalyticQContextService(repo)


@context_router.get(
    "/{repo_name}",
    response_model=AnalyticQContextModel,
    summary="Get context by repository name",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Context not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_context(
    repo_name: str,
    service: AnalyticQContextService = Depends(get_context_service)
):
    """
    Retrieve a security context by repository name.

    - **repo_name**: Name of the repository to get context for.
    - **returns**: Complete context information including repository metadata.
    """
    return await service.get_context_by_repo_name(repo_name)


@context_router.get(
    "/{repo_name}/scans",
    response_model=List[AnalyticQSASTScanResultModel],
    summary="Get scans by repository context",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Context not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_scans_by_context(
    repo_name: str,
    service: AnalyticQContextService = Depends(get_context_service)
):
    """
    Retrieve all security scans associated with a repository context.

    - **repo_name**: Name of the repository to get scans for.
    - **returns**: List of scan results associated with the repository.
    """
    return await service.get_scans_by_repo_name(repo_name)


@context_router.delete(
    "/{repo_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete context by repository name",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Context successfully deleted"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Context not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_context(
    repo_name: str,
    service: AnalyticQContextService = Depends(get_context_service)
):
    """
    Delete a security context and associated data by repository name.

    - **repo_name**: Name of the repository context to delete.
    - **returns**: No content on successful deletion.
    """
    await service.delete_context(repo_name)
