from __future__ import annotations

from typing import List

from analyticq.manager.db_manager import Base
from analyticq.validator.context import AnalyticQCodebaseType
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


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
    last_commit_hash = mapped_column(String, nullable=True)  # Provided if the repo is a remote URL

    scans: Mapped[List["AnalyticQSASTScanResult"]] = relationship("AnalyticQSASTScanResult", back_populates="context")  # type: ignore # noqa
    stats: Mapped["AnalyticQStats"] = relationship("AnalyticQStats", back_populates="context") # type: ignore # noqa
