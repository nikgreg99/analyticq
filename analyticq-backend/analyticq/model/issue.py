from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.manager.db_manager import Base
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class AnalyticQSASTIssue(Base):
    """Represents a SAST (Static Application Security Testing) issue in the AnalyticQ system.

    This class maps to the 'analyticq_sast_issues' database table and stores detailed information
    about security issues found during static code analysis.

    Attributes:
        id (int): Unique identifier for the issue (primary key)
        scan_id (str): Foreign key referencing the associated scan result
        rule_id (str): Identifier of the rule that triggered this issue
        severity (AnalyticQSeverity): Severity level of the issue
        confidence (AnalyticQConfidence): Confidence level of the issue detection
        code (str): The problematic code snippet, defaults to "Not present"
        message (str): Description of the issue, defaults to "No message"
        path (str): File path where the issue was found, defaults to "Unknown"
        start_line (int): Starting line number of the issue, defaults to 0
        end_line (int): Ending line number of the issue, defaults to 0
        column (int): Column number where the issue was found, defaults to 0
        issue_metadata (Dict[str, Any]): Additional metadata about the issue
        summary (Dict[str, Any]): Summary information about the issue
        scan_result (AnalyticQSASTScanResult): Relationship to the parent scan result

    """
    __tablename__ = "analyticq_sast_issues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("analyticq_sast_scan_results.id", ondelete="CASCADE"), index=True)
    # Rule Id can follow different convention, depending on the tool used for the analysis
    rule_id: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[AnalyticQSeverity] = mapped_column(Enum(AnalyticQSeverity), nullable=False)
    confidence: Mapped[AnalyticQConfidence] = mapped_column(Enum(AnalyticQConfidence), nullable=False)
    code: Mapped[str] = mapped_column(String, default="Not present")
    message: Mapped[str] = mapped_column(String, default="No message")
    path: Mapped[str] = mapped_column(String, default="Unknown")
    start_line: Mapped[int] = mapped_column(Integer, default=0)  # Null value means no information available
    end_line: Mapped[int] = mapped_column(Integer, default=0)  # Null value means no information available
    column: Mapped[int] = mapped_column(Integer, default=0)  # Null value means no information available
    issue_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Relationship (using forward reference)
    scan_result: Mapped["AnalyticQSASTScanResult"] = relationship("AnalyticQSASTScanResult", back_populates="issues")  # type: ignore # noqa


@event.listens_for(AnalyticQSASTIssue, 'before_insert')
def receive_before_insert_issue(mapper, connection, target):
    target.created_at = datetime.now()


@event.listens_for(AnalyticQSASTIssue, 'after_update')
def receive_before_update_issue(mapper, connection, target):
    target.updated_at = datetime.now()
