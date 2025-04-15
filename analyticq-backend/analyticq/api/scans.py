import logging
from typing import List, Optional

from analyticq.repository.scan_repository import (
    AnalyticQSASTScanResultModel, AnalyticQScanResultRepository)
from analyticq.schemas.error_dto import ErrorResponse
from analyticq.schemas.scan_dto import PaginatedScanResponse
from analyticq.service import AnalyticQScanService
from fastapi import APIRouter, Depends, Query, status

logger = logging.getLogger(__name__)

scan_router = APIRouter(prefix="/scans", tags=["Scan Management"])


def get_scan_service(
    repo: AnalyticQScanResultRepository = Depends(AnalyticQScanResultRepository)
) -> AnalyticQScanService:
    """Dependency provider for scan service."""
    return AnalyticQScanService(repo)


@scan_router.get(
    "/",
    summary="Get all scans paginated",
    response_model=PaginatedScanResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_all_scans_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Number of items per page, set to 0 for all items"),
    service: AnalyticQScanService = Depends(get_scan_service)
):
    if page_size == 0:
        scans = await service.get_all_scan()
        return {
            "items": scans,
            "total": len(scans),
            "page": 1,
            "page_size": len(scans),
            "has_more": False
        }
    else:
        # Get scans with pagination
        scans, total = await service.get_all_scans_paginated(page, page_size)
        return {
            "items": scans,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < total
        }


@scan_router.get(
    "/{scan_id}",
    response_model=AnalyticQSASTScanResultModel,
    summary="Get a scans by ID",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def get_scan_by_id(
    scan_id: int,
    service: AnalyticQScanService = Depends(get_scan_service)
):
    """
    Retrieve a list of issues for a specific scan, optionally filtered by severity and confidence.
    """
    return await service.get_scan_by_id(scan_id)


@scan_router.get(
    "/tool/{tool_name}",
    response_model=List[AnalyticQSASTScanResultModel],
    responses={
        status.HTTP_200_OK: {"description": "List of scans for the specified tool"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def get_scans_by_tool_name(
    tool_name: str,
    service: AnalyticQScanService = Depends(get_scan_service)
):
    """
    Retrieve a list of scan results for a specific SAST tool.
    """
    return await service.get_scans_by_tool_name(tool_name.lower())


@scan_router.delete(
    "/{scan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Scan successfully deleted"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def delete_scan(
    scan_id: str,
    service: AnalyticQScanService = Depends(get_scan_service)
):
    """
    Delete a scan from the database by its ID.
    """
    await service.delete_scan(scan_id)
