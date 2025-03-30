from typing import List, Optional

from analyticq.model.scan_context import AnalyticQCodebaseType
from analyticq.validator.context import AnalyticQContextModel
from pydantic import BaseModel, Field


class ContextCreateRequest(BaseModel):
    """
    Request model for creating a new context.
    """
    repo_name: str = Field(..., description="Name of the repository")
    input_type: Optional[AnalyticQCodebaseType] = Field(None, description="Type of codebase (e.g., git, local, archive)")
    branch: Optional[str] = Field(None, description="Branch name")
    last_commit_hash: Optional[str] = Field(None, description="Last commit hash")


class ContextUpdateRequest(BaseModel):
    """
    Request model for updating an existing context.
    """
    input_type: Optional[AnalyticQCodebaseType] = Field(None, description="Type of codebase (e.g., git, svn)")
    branch: Optional[str] = Field(None, description="Branch name")
    last_commit_hash: Optional[str] = Field(None, description="Last commit hash")


class PaginatedContextResponse(BaseModel):
    items: List[AnalyticQContextModel]
    total: int
    page: int
    page_size: int
    has_more: bool
