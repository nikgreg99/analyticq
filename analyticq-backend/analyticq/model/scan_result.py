from __future__ import annotations

from typing import Any, Dict, List, Optional

from analyticq.manager import AnalyticQDatabaseManager
from analyticq.manager.db_manager import Base
from sqlalchemy import JSON, String, delete, insert, select, update
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .scan_issue import AnalyticQSASTIssue


class AnalyticQSASTScanResult(Base):
    __tablename__ = "analyticq_sast_scan_results"

    scan_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    scan_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    issues: Mapped[List["AnalyticQSASTIssue"]] = relationship("AnalyticQSASTIssue",back_populates="scan_result", lazy="dynamic") # noqa

    @staticmethod
    async def get_by_scan_id(scan_id: str) -> Optional["AnalyticQSASTScanResult"]:
        """
        Retrieve a scan result by its scan_id.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            return await session.get(AnalyticQSASTScanResult, scan_id)

    @staticmethod
    async def get_all_issues_by_scan_id(scan_id: str) -> List["AnalyticQSASTIssue"]:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQSASTIssue).where(AnalyticQSASTIssue.scan_id == scan_id)
            result = await session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    async def add(scan_result_data: Dict[str, Any]) -> None:
        """
        Add a new scan result to the database.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = insert(AnalyticQSASTScanResult).values(**scan_result_data)
            await session.execute(stmt)

    @staticmethod
    async def update_by_scan_id(scan_id: str, **kwargs) -> None:
        """
        Update a scan result by its scan_id.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = update(AnalyticQSASTScanResult).where(AnalyticQSASTScanResult.scan_id == scan_id).values(**kwargs)
            await session.execute(stmt)

    @staticmethod
    async def delete_by_scan_id(scan_id: str) -> None:
        """
        Delete a scan result by its scan_id.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = delete(AnalyticQSASTScanResult).where(AnalyticQSASTScanResult.scan_id == scan_id)
            await session.execute(stmt)
