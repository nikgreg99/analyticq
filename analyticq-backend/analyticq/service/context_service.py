import logging
from typing import List

from analyticq.repository.context_repository import (
    AnalyticQContextModel, AnalyticQContextRepository)
from analyticq.repository.scan_repository import AnalyticQSASTScanResultModel
from analyticq.schemas.context_dto import (ContextCreateRequest,
                                           ContextUpdateRequest)
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AnalyticQContextService:
    """A service class for managing AnalyticQ context operations.
    This class provides methods for creating, retrieving, updating, and deleting contexts
    associated with repositories. It handles all the business logic and error handling
    for context-related operations.
    """

    def __init__(self, context_repo: AnalyticQContextRepository):
        self.context_repo = context_repo

    async def get_all_contexts(self) -> List[AnalyticQContextModel]:
        """
         Retrieves all contexts without pagination.

        Returns:
            List[AnalyticQContextModel]: A list of all context models.

        Raises:
            HTTPException: If an error occurs during retrieval, raises a 500 Internal Server Error.
        """
        try:
            contexts = await self.context_repo.get_all_contexts()
            return contexts
        except Exception as e:
            logger.error(f"Error retrieving all contexts: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving all contexts."
            )

    async def get_contexts_paginated(self, page: int, page_size: int) -> tuple[List[AnalyticQContextModel], int]:
        """
        Retrieves contexts with pagination.

        Args:
            page (int): The page number (1-indexed)
            page_size (int): The number of items per page

        Returns:
            tuple[List[AnalyticQContextModel], int]: A tuple containing:
                - List of context models for the requested page
            -    Total count of all contexts

        Raises:
            HTTPException: If an error occurs during retrieval, raises a 500 Internal Server Error.
    """
        try:
            contexts, total_count = await self.context_repo.get_contexts_paginated(page, page_size)
            return contexts, total_count
        except Exception as e:
            logger.error(f"Error retrieving paginated contexts (page={page}, page_size={page_size}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving paginated contexts."
            )

    async def create_context(self, context_data: ContextCreateRequest) -> AnalyticQContextModel:
        """
        Create a new context in the system.

        This asynchronous method handles the creation of a new context using the provided context data.
        It attempts to add the context through the repository and performs error handling.

        Args:
            context_data (ContextCreateRequest): The data required to create a new context.

        Returns:
            AnalyticQContextModel: The newly created context model.

        Raises:
            HTTPException: If the context creation fails or if there's an error during the process.
                - HTTP 500: Internal server error when context creation fails or other unexpected errors occur.
                - HTP 400: If validation fail

        Example:
            ```python
            context_data = ContextCreateRequest(repo_name="example_repo", ...)
            new_context = await create_context(context_data)
            ```
        """
        try:
            context = await self.context_repo.add(context_data)
            if not context:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve created context"
                )
            logger.info(f"Context created successfully: {context.repo_name}")
            return context
        except ValueError as e:
            logger.error(f"Validation error while creating context: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating context: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while creating the context: {str(e)}"
            )

    async def get_context_by_repo_name(self, repo_name: str) -> AnalyticQContextModel:
        """
        Retrieve a context by repository name.

        Args:
            repo_name (str): The name of the repository to get the context for.

        Returns:
            AnalyticQContextModel: The context associated with the repository.

        Raises:
            HTTPException: If context is not found (404) or if there's an internal error (500).
        """
        try:
            context = await self.context_repo.get_by_repo_name(repo_name)
            if not context:
                logger.error(f"Context with repository name {repo_name} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Context with name {repo_name} not found"
                )
            return context
        except Exception as e:
            logger.error(f"Unexpected error while retrieving context for repository {repo_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while retrieving the context: {str(e)}"
            )

    async def get_scans_by_repo_name(self, repo_name: str) -> List[AnalyticQSASTScanResultModel]:
        """
        Retrieves a list of SAST scan results for a specific repository.

        Args:
            repo_name (str): The name of the repository to get scans for.

        Returns:
            List[AnalyticQSASTScanResultModel]: A list of scan result models associated with the repository.
                Returns an empty list if no scans are found.

        Raises:
            HTTPException: If an error occurs while retrieving the scans from the repository.
                Returns a 500 Internal Server Error with an error message.
        """
        try:
            scans = await self.context_repo.get_scans_by_repo_name(repo_name)
            return scans or []
        except Exception as e:
            logger.error(f"Error retrieving scans for repository {repo_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving scans."
            )

    async def update_context(self, repo_name: str, update_data: ContextUpdateRequest) -> AnalyticQContextModel:
        """
        Updates the context information for a specified repository.
        Args:
            repo_name (str): The name of the repository whose context needs to be updated.
            update_data (ContextUpdateRequest): The data containing the fields to be updated.
        Returns:
            AnalyticQContextModel: The updated context model.
        Raises:
            HTTPException: If the context is not found or if there's an error during update.
                - HTTP 404 if context not found
                - HTTP 500 for other update errors
                - HTTP 440 if request is not valid
        """
        try:
            context = await self.context_repo.update_by_repo_name(repo_name, **update_data.model_dump(exclude_unset=True))
            if not context:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Context with repository name {repo_name} not found"
                )
            logger.info(f"Context updated successfully: {repo_name}")
            return context
        except ValueError as e:
            logger.error(f"Validation error while updating context: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error updating context for repository {repo_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the context"
            )

    async def delete_context(self, repo_name: str) -> None:
        """
        Delete a context associated with a repository name.

        Args:
            repo_name (str): The name of the repository whose context should be deleted.

        Raises:
            HTTPException: If an error occurs during deletion, raises a 500 Internal Server Error.

        Returns:
            None
        """
        try:
            await self.context_repo.delete_by_repo_name(repo_name)
            logger.info(f"Context deleted successfully: {repo_name}")
        except Exception as e:
            logger.error(f"Error deleting context for repository {repo_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the context."
            )
