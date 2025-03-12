from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CodebaseType(str, Enum):
    REMOTE = "remote"  # Remote Git repository
    REPO = "repo"      # Local Git repository
    LOCAL_DIR = "local"  # Local directory (not a Git repo)
    SCRIPT = "script"  # Script or file


class AnalyticQScanContextModel(BaseModel):
    """
    Context class for storing repository scan-related information.
    """
    input_type: CodebaseType  # Type of input (remote, repo, local, script)
    repo_name: str
    branch: Optional[str] = None
    last_commit_hash: Optional[str] = None

    class Config:
        from_attributes = True
