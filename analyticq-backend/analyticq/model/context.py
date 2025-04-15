from __future__ import annotations

from datetime import datetime
from typing import List

from analyticq.manager.db_manager import Base
from analyticq.validator.context import AnalyticQCodebaseType
from sqlalchemy import DateTime, Enum, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class AnalyticQContext(Base):
    """
    A class representing the context of a code analysis scan in AnalyticQ.

    This class stores information about the repository being analyzed, including its name,
    type, branch, and commit hash for version control tracking. It also maintains relationships
    with scan results and preproacessing analysis.

    Attributes:
        id (int): The primary key identifier for the context.
        repo_name (str): The unique name of the repository being analyzed.
        input_type (AnalyticQCodebaseType): The type of codebase being analyzed (enum).
        branch (str): The branch name for remote repositories.
        last_commit_hash (str): The hash of the last commit for remote repositories.
        scans (List[AnalyticQSASTScanResult]): Related SAST scan results.
        stats (AnalyticQPreprocessingAnalysis): Related preprocessing analysis.
    """

    __tablename__ = "analyticq_scan_context"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    repo_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    input_type = mapped_column(Enum(AnalyticQCodebaseType), nullable=True)
    branch: Mapped[str] = mapped_column(String, nullable=True)  # Provide if the repo is a remote URL
    last_commit_hash: Mapped[str] = mapped_column(String, nullable=True)  # Provided if the repo is a remote URL

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())


    scans: Mapped[List["AnalyticQSASTScanResult"]] = relationship("AnalyticQSASTScanResult", back_populates="context")  # type: ignore # noqa
    stats: Mapped["AnalyticQStats"] = relationship("AnalyticQStats", back_populates="context") # type: ignore # noqa


@event.listens_for(AnalyticQContext, 'before_insert')
def receive_before_insert_context(mapper, connection, target):
    target.created_at = datetime.now()


@event.listens_for(AnalyticQContext, 'after_update')
def receive_before_update_context(mapper, connetction, target):
    target.updated_at = datetime.now()
