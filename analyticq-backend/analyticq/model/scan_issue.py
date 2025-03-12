from __future__ import annotations

from typing import Any, Dict, List, Optional

from analyticq.engine.core import (AnalyticQConfidence,
                                   AnalyticQSASTIssueModel, AnalyticQSeverity)
from analyticq.manager import AnalyticQDatabaseManager
from analyticq.manager.db_manager import Base
from sqlalchemy import (JSON, Enum, ForeignKey, Integer, String, delete,
                        insert, select, update)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AnalyticQSASTIssue(Base):
    __tablename__ = "analyticq_sast_issues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    scan_id: Mapped[str] = mapped_column(ForeignKey("analyticq_sast_scan_results.scan_id"), nullable=False)
    # Id can follow different convention, depending on the tool used for the analysis
    rule_id: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(Enum(AnalyticQSeverity), nullable=False)
    confidence: Mapped[str] = mapped_column(Enum(AnalyticQConfidence), nullable=False)
    code: Mapped[str] = mapped_column(String, default="Not present")
    message: Mapped[str] = mapped_column(String, default="No message")
    path: Mapped[str] = mapped_column(String, default="unknown")
    start_line: Mapped[int] = mapped_column(Integer, default=0)  # A 0 value means no information available
    end_line: Mapped[int] = mapped_column(Integer, default=0)  # A 0 value means no information available
    column: Mapped[int] = mapped_column(Integer, default=0)  # A 0 value means no information available
    issue_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=None)
    summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=None)

    # Relationship (using forward reference)
    scan_result: Mapped["AnalyticQSASTScanResult"] = relationship("AnalyticQSASTScanResult", back_populates="issues")  # type: ignore # noqa

    @staticmethod
    async def get_by_id(issue_id: int) -> Optional["AnalyticQSASTIssueModel"]:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            return await session.get(AnalyticQSASTIssueModel, issue_id)

    @staticmethod
    async def get_multiple_by_ids(issue_ids: List[int]) -> List["AnalyticQSASTIssue"]:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQSASTIssue).where(AnalyticQSASTIssue.id.in_(issue_ids))
            result = await session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    async def add(issue_data: "AnalyticQSASTIssueModel") -> None:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = insert(AnalyticQSASTIssueModel).values(**issue_data.dict())
            await session.execute(stmt)

    @staticmethod
    async def update_by_id(issue_id: int, **kwargs) -> None:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = update(AnalyticQSASTIssue).where(AnalyticQSASTIssue.id == issue_id).values(**kwargs)
            await session.execute(stmt)

    @staticmethod
    async def delete_by_id(issue_id: int) -> None:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = delete(AnalyticQSASTIssue).where(AnalyticQSASTIssue.id == issue_id)
            await session.execute(stmt)
