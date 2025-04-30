from typing import Dict, Optional

from pydantic import BaseModel


class GitRepoRequest(BaseModel):
    """
    A model representing a request to analyze a Git repository.

    Attributes:
        git_url (str): The URL of the Git repository to analyze.
        branch (Optional[str]): The specific branch to analyze. If None, defaults to the main branch.
        config_paths (Optional[Dict[str, str]]): Dictionary mapping configuration names to their file paths.
            Example: {"sonarqube": "/path/to/sonar-project.properties"}
        timeout (Optional[int]): Maximum time in seconds to wait for the analysis to complete.
            If None, no timeout is applied.
    """
    git_url: str
    branch: Optional[str] = None
    config_paths: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None


class AnalysisResponse(BaseModel):
    """
    A Pydantic model representing the response of an analysis operation.

    Attributes:
        analysis_id (str): The unique identifier of the analysis.
        status (str): The current status of the analysis.
    """
    analysis_id: str
    status: str
