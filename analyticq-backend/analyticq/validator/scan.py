from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .issue import AnalyticQSASTIssueModel


class AnalyticQSASTScanResultModel(BaseModel):
    """
    Contains results of a SAST scan in AnalyticQ.

    Attributes:
        scan_id (str): Unique identifier for the scan
        context (AnalyticQScanContext): Scan execution context
        issues (List[AnalyticQSASTIssue]): List of discovered security issues
        summary (Dict[str, Any]): Aggregated scan statistics
        metadata (Dict[str, Any]): Additional scan metadata

    """
    id: Optional[int] = None
    scan_id: str
    context_id: Optional[int] = None
    tool_name: Optional[str] = None
    issues: List[AnalyticQSASTIssueModel] = []
    summary: Dict[str, Any] = Field(default_factory=dict)
    scan_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
