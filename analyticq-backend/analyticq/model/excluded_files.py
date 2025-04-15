from analyticq.manager.db_manager import Base
from sqlalchemy import JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column


class AnalyticQExcludedFiles(Base):
    """Represents excluded files data in the AnalyticQ system.
    This class maps to the 'analyticq_excluded_files' database table and stores information
    about files that were excluded from analysis.
    Attributes:
        id (int): Primary key identifier for the record.
        count (int): Number of excluded files.
        total_size (int): Total size in bytes of all excluded files.
        files (dict): JSON structure containing details about the excluded files.
    """
    __tablename__ = "analyticq_excluded_files"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True, autoincrement=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_size: Mapped[int] = mapped_column(Integer, nullable=False)
    files: Mapped[list] = mapped_column(JSON, nullable=False, default=[])
