from typing import List, Optional

from analyticq.model.context import AnalyticQCodebaseType
from analyticq.validator.context import AnalyticQContextModel
from pydantic import BaseModel, Field


class ContextCreateRequest(BaseModel):
    """
    A data model representing a request to create a context for code analysis.

    This class inherits from BaseModel and defines the structure for creating
    a new context with repository information.

    Attributes:
        repo_name (str): The name of the repository to analyze.
        input_type (AnalyticQCodebaseType, optional): Specifies the type of codebase,
            such as git repository, local directory, or archive file.
        branch (str, optional): The name of the branch to analyze.
        last_commit_hash (str, optional): The hash of the last commit in the repository.
    """
    repo_name: str = Field(..., description="Name of the repository")
    input_type: Optional[AnalyticQCodebaseType] = Field(None, description="Type of codebase (e.g., git, local, archive)")
    branch: Optional[str] = Field(None, description="Branch name")
    last_commit_hash: Optional[str] = Field(None, description="Last commit hash")


class ContextUpdateRequest(BaseModel):
    """
    A request model for updating context information in an AnalyticQ codebase.
    This model extends BaseModel and provides optional fields for updating context-specific
    information related to a codebase, including its type, branch, and commit details.
    Attributes:
        input_type (AnalyticQCodebaseType, optional): Specifies the type of the codebase
            (e.g., git, archive)
        branch (str, optional): The name of the branch to be updated
        last_commit_hash (str, optional): The hash of the most recent commit
    """
    input_type: Optional[AnalyticQCodebaseType] = Field(None, description="Type of codebase (e.g., git, archive)")
    branch: Optional[str] = Field(None, description="Branch name")
    last_commit_hash: Optional[str] = Field(None, description="Last commit hash")


class PaginatedContextResponse(BaseModel):
    """A model representing a paginated response for AnalyticQContext items.

    Attributes:
        items (List[AnalyticQContextModel]): List of context items for the current page
        total (int): Total number of items across all pages
        page (int): Current page number
        page_size (int): Number of items per page
        has_more (bool): Indicates whether more items exist in subsequent pages
    """
    items: List[AnalyticQContextModel]
    total: int
    page: int
    page_size: int
    has_more: bool
