from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from analyticq.manager.db_manager import Base
from analyticq.model.issue import AnalyticQSASTIssue
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


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
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[str] = mapped_column(String, index=True)
    tool_name: Mapped[str] = mapped_column(String, index=True, default="Unknown")
    context_id: Mapped[Optional[int]] = mapped_column(ForeignKey("analyticq_scan_context.id", ondelete="CASCADE"))
    summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    scan_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())

    issues: Mapped[List["AnalyticQSASTIssue"]] = relationship("AnalyticQSASTIssue", back_populates="scan_result", cascade="all, delete-orphan",
    passive_deletes=True) # noqa
    context: Mapped["AnalyticQContext"] = relationship("AnalyticQContext", back_populates="scans") # type: ignore # noqa


@event.listens_for(AnalyticQSASTScanResult, 'before_insert')
def receive_before_insert_scan(mapper, connection, target):
    target.created_at = datetime.now()


@event.listens_for(AnalyticQSASTScanResult, 'after_update')
def receive_before_update_scan(mapper, connetction, target):
    target.updated_at = datetime.now()
