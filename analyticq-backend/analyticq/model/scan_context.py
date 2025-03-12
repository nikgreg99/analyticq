from typing import List, Optional

from analyticq.manager import AnalyticQDatabaseManager
from analyticq.manager.db_manager import Base
from analyticq.preprocessing.models import (AnalyticQScanContextModel,
                                            CodebaseType)
from sqlalchemy import Enum, String, delete, insert, select, update
from sqlalchemy.orm import Mapped, mapped_column


class AnalyticQScanContext(Base):

    __tablename__ = "analyticq_scan_context"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    repo_name: Mapped[str] = mapped_column(String, nullable=False)
    input_type = mapped_column(Enum(CodebaseType), nullable=True)
    branch: Mapped[str] = mapped_column(String, nullable=True)
    last_commit_hash = mapped_column(String, nullable=True)

    @staticmethod
    async def get_by_repo_name(repo_name: str) -> Optional["AnalyticQScanContext"]:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            return await session.get(AnalyticQScanContext, repo_name)

    @staticmethod
    async def get_multiple_by_repo_name(repo_names: List[str]) -> List["AnalyticQScanContext"]:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQScanContext).where(AnalyticQScanContext.repo_name.in_(repo_names))
            result = await session.execute(stmt)
            return result.all()

    @staticmethod
    async def add(context_data: "AnalyticQScanContextModel") -> None:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = insert(AnalyticQScanContext).values(**context_data.dict())
            await session.execute(stmt)

    @staticmethod
    async def update_by_repo_name(repo_name: str, **kwargs) -> None:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = update(AnalyticQScanContext).where(AnalyticQScanContext.repo_name == repo_name).values(**kwargs)
            await session.execute(stmt)

    @staticmethod
    async def delete_by_repo_name(repo_name: str) -> None:
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = delete(AnalyticQScanContext).where(AnalyticQScanContext.repo_name == repo_name)
            await session.execute(stmt)
