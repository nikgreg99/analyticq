from typing import Any, Dict, List, Optional

from analyticq.validator.issue import AnalyticQSASTIssueModel
from analyticq.validator.scan import AnalyticQSASTScanResultModel
from pydantic import BaseModel, Field


class ScanCreateRequest(BaseModel):
    id: Optional[int] = None
    scan_id: str
    context_id: Optional[int] = None
    tool_name: Optional[str] = None
    issues: List[AnalyticQSASTIssueModel] = []
    summary: Dict[str, Any] = Field(default_factory=dict)
    scan_metadata: Dict[str, Any] = Field(default_factory=dict)


class ScanUpdateRequest(BaseModel):
    """
    A data model representing a request to update a scan in the AnalyticQ system.

    Attributes:
        id (Optional[int]): The database ID of the scan record. Defaults to None.
        scan_id (str): A unique identifier for the scan.
        context_id (Optional[int]): The ID of the associated context. Defaults to None.
        tool_name (Optional[str]): The name of the scanning tool used. Defaults to None.
        issues (List[AnalyticQSASTIssueModel]): List of security issues found during scan. Defaults to empty list.
        summary (Dict[str, Any]): Summary information about the scan results. Defaults to empty dict.
        scan_metadata (Dict[str, Any]): Additional metadata about the scan. Defaults to empty dict.
    """
    id: Optional[int] = None
    scan_id: Optional[str] = None
    context_id: Optional[int] = None
    tool_name: Optional[str] = None
    issues: List[AnalyticQSASTIssueModel] = []
    summary: Dict[str, Any] = Field(default_factory=dict)
    scan_metadata: Dict[str, Any] = Field(default_factory=dict)


class PaginatedScanResponse(BaseModel):
    """A model representing a paginated response for scan results.

        items (List[AnalyticQSASTScanResultModel]): List of scan result items for the current page
        total (int): Total number of scan result items across all pages
        page (int): Current page number (1-based indexing)
        page_size (int): Maximum number of items included per page
        has_more (bool): Indicates if there are more pages of results available
    """
    items: List[AnalyticQSASTScanResultModel]
    total: int
    page: int
    page_size: int
    has_more: bool
