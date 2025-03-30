from analyticq.manager.db_manager import Base
from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class AnalyticQCodebaseLanguageStatistics(Base):
    """
    A SQLAlchemy model representing statistics about programming languages in a codebase.
    This class stores various metrics and statistics about programming language usage,
    including file counts, sizes, and distribution metrics.
    Attributes:
        id (int): Primary key identifier for the statistics entry
        language (str): Name of the programming language
        file_count (int): Total number of files in this language
        total_size (int): Total size of all files in this language (in bytes)
        largest_file (dict): Information about the largest file in this language
        smallest_file (dict): Information about the smallest file in this language
        average_size (float): Average file size for this language
        median_size (float): Median file size for this language
        std_size (float): Standard deviation of file sizes for this language
        percentage_files (float): Percentage of total codebase files in this language
    """

    __tablename__ = "analyticq_codebase_language_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    language: Mapped[str] = mapped_column(String, nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_size: Mapped[int] = mapped_column(Integer, nullable=False)
    largest_file: Mapped[dict] = mapped_column(JSON, nullable=False)
    smallest_file: Mapped[dict] = mapped_column(JSON, nullable=False)
    average_size: Mapped[float] = mapped_column(Float, nullable=False)
    median_size: Mapped[float] = mapped_column(Float, nullable=False)
    std_size: Mapped[float] = mapped_column(Float, nullable=False)
    percentage_files: Mapped[Float] = mapped_column(Float, nullable=False)
