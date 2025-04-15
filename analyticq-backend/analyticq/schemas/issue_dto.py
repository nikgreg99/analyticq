from typing import Any, Dict, List, Optional

from analyticq.engine import AnalyticQConfidence, AnalyticQSeverity
from analyticq.validator.issue import AnalyticQSASTIssueModel
from pydantic import BaseModel, Field


class IssueCreateRequest(BaseModel):
    """
    Request DTO for creating a new issue.
    """
    id: int
    scan_id: str
    rule_id: str
    severity: AnalyticQSeverity
    confidence: AnalyticQConfidence
    code: str = Field(default="Not present")
    message: str = Field(default="No message")
    path: str = Field(default="Unknown")
    start_line: int = Field(default=0, ge=0)
    end_line: int = Field(default=0, ge=0)
    column: int = Field(default=0, ge=0)
    issue_metadata: Dict[str, Any] = Field(default={})
    summary: Dict[str, Any] = Field(default={})


class IssueUpdateRequest(BaseModel):
    """
    Request DTO for updating an existing issue.
    """
    rule_id: Optional[str] = None
    severity: Optional[AnalyticQSeverity] = None
    confidence: Optional[AnalyticQConfidence] = None
    code: Optional[str] = None
    message: Optional[str] = None
    path: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    column: Optional[int] = None
    issue_metadata: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True  # Enable ORM mode for Pydantic


class IssueFilter(BaseModel):
    """
    DTO for filtering issues by severity and confidence.
    """
    severity: Optional[AnalyticQSeverity] = None
    confidence: Optional[AnalyticQConfidence] = None


class PaginatedIssueResponse(BaseModel):
    """A model representing a paginated response for AnalyticQContext items.

    Attributes:
        items (List[AnalyticQContextModel]): List of context items for the current page
        total (int): Total number of items across all pages
        page (int): Current page number
        page_size (int): Number of items per page
        has_more (bool): Indicates whether more items exist in subsequent pages
    """
    items: List[AnalyticQSASTIssueModel]
    total: int
    page: int
    page_size: int
    has_more: bool
