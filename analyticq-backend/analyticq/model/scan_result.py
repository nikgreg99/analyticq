from __future__ import annotations

from typing import Any, Dict, List, Optional

from analyticq.manager.db_manager import Base
from analyticq.model.issue import AnalyticQSASTIssue
from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AnalyticQSASTScanResult(Base):
    """
    A class representing a SAST scan result in the AnalyticQ system.

    This class manages scanning results from Static Application Security Testing (SAST),
    storing the scan ID, summary, metadata and related security issues found during the scan.

    Attributes:
        scan_id (str): Unique identifier for the scan result
        summary (Dict[str, Any]): Dictionary containing scan result summary
        scan_metadata (Dict[str, Any]): Dictionary containing metadata about the scan
        issues (List[AnalyticQSASTIssue]): List of security issues found during the scan

    """
    __tablename__ = "analyticq_sast_scan_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[str] = mapped_column(String, index=True)
    tool_name: Mapped[str] = mapped_column(String, index=True, default="Unknown")
    context_id: Mapped[Optional[int]] = mapped_column(ForeignKey("analyticq_scan_context.id"))
    summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    scan_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    issues: Mapped[List["AnalyticQSASTIssue"]] = relationship("AnalyticQSASTIssue", back_populates="scan_result") # noqa
    context: Mapped["AnalyticQContext"] = relationship("AnalyticQContext", back_populates="scans") # type: ignore # noqa
