from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AnalyticQCodebaseType(str, Enum):
    """Enum class representing different types of codebases that can be analyzed.

    The CodebaseType enum defines the various source types that the analysis can be performed on:

    Attributes:
        ARCHIVE (str): A compressed archive file (e.g., .zip, .tar.gz)
        REMOTE (str): A remote Git repository accessed via URL
        REPO (str): A local Git repository on the filesystem
        LOCAL_DIR (str): A local directory that is not a Git repository
        SCRIPT (str): A single script or file to be analyzed
    """
    ARCHIVE = "archive"  # Compressed archive file
    REMOTE = "remote"  # Remote Git repository
    REPO = "repo"      # Local Git repository
    LOCAL_DIR = "local"  # Local directory (not a Git repo)
    SCRIPT = "script"  # Script or file


class AnalyticQContextModel(BaseModel):
    """
    Context class for storing repository scan-related information.
    """
    id: Optional[int] = None  # Add the id attribute
    repo_name: str
    input_type: Optional[AnalyticQCodebaseType] = None  # Type of input (remote, repo, local, script or acrchive)
    branch: Optional[str] = None  # Only for Git repositories (default one is main/master)
    last_commit_hash: Optional[str] = None  # Only for Git repositories

    class Config:
        from_attributes = True
