from datetime import datetime
from typing import Dict, List

from analyticq.manager.db_manager import Base
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .excluded_files import AnalyticQExcludedFiles


class AnalyticQStats(Base):
    """A SQLAlchemy model representing analysis data of a codebase.
    This class defines the schema for storing codebase analysis metrics and exclusion settings
    in the database.
    Attributes:
        id (int): Primary key identifier for the analysis record.
        total_files_scanned (int): Total number of files that were analyzed.
        total_size_scanned (int): Total size of all scanned files in bytes.
        excluded_directories (dict): Dictionary containing directories excluded from analysis.
        excluded_files_id (int): Foreign key reference to excluded files configuration.
        excluded_files (AnalyticQExcludedFiles): Relationship to the excluded files configuration.
    """
    __tablename__ = "analyticq_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    context_id: Mapped[int] = mapped_column(Integer, ForeignKey("analyticq_scan_context.id", ondelete="CASCADE"), nullable=True)
    total_files_scanned: Mapped[int] = mapped_column(Integer, nullable=False)
    total_size_scanned : Mapped[int] = mapped_column(Integer, nullable=False)
    excluded_directories: Mapped[list] = mapped_column(JSON, nullable=False, default=[])
    excluded_files_id: Mapped[int] = mapped_column(Integer, ForeignKey("analyticq_excluded_files.id"))
    language_statistics: Mapped[dict] = mapped_column(JSON, nullable=True, default={})
    files: Mapped[List[Dict]] = mapped_column(JSON, nullable=True, default=[])

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())

    excluded_files: Mapped["AnalyticQExcludedFiles"] = relationship("AnalyticQExcludedFiles")
    context: Mapped["AnalyticQContext"] = relationship("AnalyticQContext", back_populates="stats") # type: ignore # noqa


@event.listens_for(AnalyticQStats, 'before_insert')
def receive_before_insert_scan(mapper, connection, target):
    target.created_at = datetime.now()


@event.listens_for(AnalyticQStats, 'after_update')
def receive_before_update_scan(mapper, connetction, target):
    target.updated_at = datetime.now()
