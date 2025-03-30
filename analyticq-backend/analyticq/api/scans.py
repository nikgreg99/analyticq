import logging
from enum import Enum
from typing import List, Optional

from analyticq.repository.scan_repository import (
    AnalyticQSASTIssueModel, AnalyticQSASTScanResultModel,
    AnalyticQScanResultRepository)
from analyticq.schemas.scan_dto import ScanCreateRequest
from analyticq.service import AnalyticQScanService
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

scan_router = APIRouter(prefix="/scans", tags=["Scan Management"])


class ErrorResponse(BaseModel):
    detail: str


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class Confidence(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


def get_scan_service(
    repo: AnalyticQScanResultRepository = Depends(AnalyticQScanResultRepository)
) -> AnalyticQScanService:
    """Dependency provider for scan service."""
    return AnalyticQScanService(repo)


@scan_router.post(
    "/",
    response_model=AnalyticQSASTScanResultModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Scan created successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def create_scan(
    scan_data: ScanCreateRequest,
    service: AnalyticQScanService = Depends(get_scan_service)
):
    """
    Create a new scan record in the system.
    """
    return await service.create_scan(scan_data)


@scan_router.get(
    "/{scan_id}/issues",
    response_model=List[AnalyticQSASTIssueModel],
    responses={
        status.HTTP_200_OK: {"description": "List of filtered issues"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def get_filtered_scan_issues(
    scan_id: str,
    severity: Optional[Severity] = Query(None, description="Filter issues by severity"),
    confidence: Optional[Confidence] = Query(None, description="Filter issues by confidence"),
    service: AnalyticQScanService = Depends(get_scan_service)
):
    """
    Retrieve a list of issues for a specific scan, optionally filtered by severity and confidence.
    """
    return await service.filter_scan_issues(scan_id, severity, confidence)


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
    return await service.get_scans_by_tool_name(tool_name)


@scan_router.get(
    "/tool/{tool_name}/issues",
    response_model=List[AnalyticQSASTIssueModel],
    responses={
        status.HTTP_200_OK: {"description": "List of issues for the specified tool"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def get_scan_issues_by_tool_name(
    tool_name: str,
    service: AnalyticQScanService = Depends(get_scan_service)
):
    """
    Retrieve all issues found by a specific security analysis tool.
    """
    return await service.get_issues_by_tool_name(tool_name)


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
