import logging
from typing import List, Optional

from analyticq.repository.issue_repository import (
    AnalyticQSASTIssueModel, AnalyticQSASTIssueRepository)
from analyticq.schemas.issue_dto import IssueCreateRequest, IssueUpdateRequest
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AnalyticQSASTIssueService:
    """
    Service class for managing SAST (Static Application Security Testing) issues in AnalyticQ.
    This class provides methods for creating, retrieving, updating, filtering and deleting SAST issues.
    It acts as an intermediary layer between the API controllers and the data repository.
    """

    def __init__(self, issue_repository: "AnalyticQSASTIssueRepository"):
        self.issue_repo = issue_repository

    async def get_all_issues(self) -> List[AnalyticQSASTIssueModel]:
        try:
            return await self.issue_repo.get_all_issues()
        except Exception as e:
            logger.error(f"Error getting all issues: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting all issues: {str(e)}"
            )

    async def get_all_issues_paginated(self, offset, limit) -> List[AnalyticQSASTIssueModel]:
        """
        Retrieves a paginated list of SAST issues from the database.

        Args:
            offset (int): The number of records to skip before starting to collect results.
            limit (int): The maximum number of records to return.

        Returns:
            List[AnalyticQSASTIssueModel]: A list of SAST issue models within the specified pagination range.

        Raises:
            HTTPException:
                - HTTP 404 if no issues are found in the database
                - HTTP 500 if there's an internal server error during retrieval
        """
        try:
            issues, total_counts = await self.issue_repo.get_all_issues_paginated(offset, limit)
            if not issues:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Issue table is empty:"
                )
            return issues, total_counts
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting paginated issues: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting paginated issues: {str(e)}"
            )

    async def get_issue(self, issue_id: int) -> AnalyticQSASTIssueModel:
        """
        Retrieves a specific SAST issue by its ID.
        Args:
            issue_id (int): The unique identifier of the SAST issue to retrieve.
        Returns:
            AnalyticQSASTIssueModel: The SAST issue data model if found.
        Raises:
            HTTPException: If issue is not found (404) or if there's a server error (500).
        """
        try:

            issue = await self.issue_repo.get_issue_by_id(issue_id)
            if not issue:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Issue {issue_id} not found"
                )
            return issue
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting issue {issue_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting issue: {str(e)}"
            )

    async def create_issue(self, issue_data: IssueCreateRequest) -> AnalyticQSASTIssueModel:
        """
        Creates a new SAST issue in the system.

        Args:
            issue_data (IssueCreateRequest): The data for creating the new issue.

        Returns:
            AnalyticQSASTIssueModel: The newly created issue.

        Raises:
            HTTPException: If there is an error creating the issue or retrieving the created issue.
                - HTTP 500: Internal server error when issue creation fails or cannot be retrieved.
        """
        try:
            issue = await self.issue_repo.add_issue(issue_data)
            if not issue:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve created issue"
                )
            return issue
        except ValueError as e:
            logger.error(f"Validation error while creating issue: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.info(f"Issue created successfully: {issue.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating issue: {str(e)}"
            )

    async def create_multiple_issue(self, issues_data: List[IssueCreateRequest]) -> List[AnalyticQSASTIssueModel]:
        try:
            issues = await self.issue_repo.add_multiple_issues([AnalyticQSASTIssueModel(**issue.model_dump()) for issue in issues_data])
            if not issues:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve created issues"
                )
            return issues
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"Validation error while creating multiple issues: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating multiple issues: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating multiple issues: {str(e)}"
            )

    async def update_issue(self, issue_id: int, updated_data: IssueUpdateRequest) -> AnalyticQSASTIssueModel:
        """
        Updates an existing issue with the provided data.

        Args:
            issue_id (int): The ID of the issue to update.
            updated_data (IssueUpdateRequest): The data to update the issue with.

        Returns:
            AnalyticQSASTIssueModel: The updated issue model.

        Raises:
            HTTPException:
                - 404: If the issue is not found after update.
                - 500: If there's an error during the update process.
        """
        try:
            issue = await self.issue_repo.update_issue_by_id(issue_id, **updated_data.model_dump(exclude_unset=True))
            if not issue:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Failed to retrieve updated issue {issue_id}"
                )
            logger.info(f"Issue updated successfully: {issue.id}")
            return issue
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"Validation error while updating issue: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating issue: {str(e)}"
            )

    async def filter_scan_issues(
            self,
            scan_id: str,
            severity: Optional[str] = None,
            confidence: Optional[str] = None
    ) -> List[AnalyticQSASTIssueModel]:
        """
            Filter and retrieve SAST issues for a specific scan based on severity and confidence levels.
            Args:
                scan_id (str): The unique identifier of the scan to filter issues from
                severity (Optional[str]): Filter issues by severity level (e.g., 'HIGH', 'MEDIUM', 'LOW')
                confidence (Optional[str]): Filter issues by confidence level (e.g., 'HIGH', 'MEDIUM', 'LOW')
            Returns:
                List[AnalyticQSASTIssueModel]: A list of filtered SAST issues matching the criteria
            Raises:
                HTTPException: If there is an error retrieving the issues, with status code 500
        """
        try:
            issues = await self.issue_repo.filter_scan_issues(scan_id, severity, confidence)
            return issues
        except Exception as e:
            logger.error(f"Error retrieving issues for scan {scan_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving issues {str(e)}"
            )

    async def delete_issue(self, issue_id: int) -> None:
        """
        Delete an issue from the database by its ID.

        Args:
            issue_id (int): The unique identifier of the issue to delete.

        Raises:
            HTTPException: If there is an error deleting the issue from the database.
                Returns 500 status code with error details.

        Returns:
            None
        """
        try:
            deleted = await self.issue_repo.delete_issue_by_id(issue_id)
            if not deleted:
                logger.error(f"Issue {issue_id} not found during deletion.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Issue {issue_id} not found."
                )
            logger.info(f"Issue deleted successfully: {issue_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while deleting issue {issue_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting the issue."
            )
