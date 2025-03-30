from typing import Dict, List

from analyticq.manager.db_manager import Base
from sqlalchemy import JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    context_id: Mapped[int] = mapped_column(Integer, ForeignKey("analyticq_scan_context.id"), nullable=True)
    total_files_scanned: Mapped[int] = mapped_column(Integer, nullable=False)
    total_size_scanned : Mapped[int] = mapped_column(Integer, nullable=False)
    excluded_directories: Mapped[list] = mapped_column(JSON, nullable=False, default=[])
    excluded_files_id: Mapped[int] = mapped_column(Integer, ForeignKey("analyticq_excluded_files.id"))
    language_statistics: Mapped[dict] = mapped_column(JSON, nullable=True, default={})
    files: Mapped[List[Dict]] = mapped_column(JSON, nullable=True, default=[])

    excluded_files: Mapped["AnalyticQExcludedFiles"] = relationship("AnalyticQExcludedFiles")
    context: Mapped["AnalyticQContext"] = relationship("AnalyticQContext", back_populates="stats") # type: ignore # noqa
