from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional


class AnalysisStatus(str, Enum):
    """Enumeration class representing the possible states of an analysis.

    This enum defines the various statuses that an analysis can have during its lifecycle.

    Attributes:
        PENDING (str): Initial state when analysis is queued but not yet started.
        RUNNING (str): State indicating the analysis is currently in progress.
        COMPLETED (str): State indicating the analysis has finished successfully.
        FAILED (str): State indicating the analysis encountered an error and failed.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalysisRecord:
    """
    A class representing a record of an analysis performed on code.

    Attributes:
        analysis_id (str): Unique identifier for the analysis.
        status (AnalysisStatus): Current status of the analysis.
        created_at (float): Timestamp when the analysis was created.
        analysis_type (str): Type of analysis performed.
        temp_files (List[str]): List of temporary files created during analysis.
        temp_dir (Optional[str]): Temporary directory path used for analysis.
        original_filenames (List[str]): List of original filenames analyzed.
        git_url (Optional[str]): URL of the git repository being analyzed.
        results (Optional[Any]): Results of the analysis.
        error (Optional[str]): Error message if analysis failed.
    """
    analysis_id: str
    status: AnalysisStatus
    created_at: float
    analysis_type: str
    temp_files: List[str] = field(default_factory=list)
    temp_dir: Optional[str] = None
    original_filenames: List[str] = field(default_factory=list)
    git_url: Optional[str] = None
    results: Optional[Any] = None
    error: Optional[str] = None
