from __future__ import annotations

from typing import List, Optional

from analyticq.engine.core import AnalyticQSASTIssueModel
from analyticq.manager import AnalyticQDatabaseManager
from analyticq.model.issue import AnalyticQSASTIssue
from sqlalchemy import and_, delete, func, insert, select, update


class AnalyticQSASTIssueRepository:
    """
    Methods:
        get_by_id(issue_id: int) -> Optional[AnalyticQSASTIssueModel]:
            Retrieves an issue by its ID asynchronously.

        add(issue_data: AnalyticQSASTIssueModel) -> None:
            Adds a new issue to the database asynchronously.

        update_by_id(issue_id: int, **kwargs) -> None:
            Updates an existing issue by its ID asynchronously.

        delete_by_id(issue_id: int) -> None:
            Deletes an issue by its ID asynchronously.
    """

    async def get_all_issues(self) -> List[AnalyticQSASTIssueModel]:
        """
        Retrieves all contexts from the database without pagination.

        Returns:
            List[AnalyticQContextModel]: A list of all context models in the database.

        Example:
            contexts = await context_repository.get_all_contexts()
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQSASTIssue)
            result = await session.execute(stmt)
            contexts = result.scalars().all()
            return [AnalyticQSASTIssueModel.model_validate(context) for context in contexts]

    async def get_all_issues_paginated(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[AnalyticQSASTIssueModel]:
        """
        Retrieves a paginated list of all SAST issues from the database.

        This method fetches SAST issues with pagination support, returning both the issues
        and the total count of all issues in the database.

        Args:
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            Tuple[List[AnalyticQSASTIssueModel], int]: A tuple containing:
                - List of SAST issues as AnalyticQSASTIssueModel objects
                - Total count of all issues in the database

        Example:
            issues, total = await repo.get_all_issues_paginated(offset=20, limit=10)
        """

        async with AnalyticQDatabaseManager().get_db_session() as session:

            count_stmt = select(func.count()).select_from(AnalyticQSASTIssue)
            count_result = await session.execute(count_stmt)
            total_count = count_result.scalar_one()

            query = select(AnalyticQSASTIssue).offset(offset).limit(limit)
            result = await session.execute(query)
            issues = result.scalars().all()
            return [AnalyticQSASTIssueModel.model_validate(issue) for issue in issues], total_count

    async def get_issue_by_id(self, issue_id: int) -> Optional["AnalyticQSASTIssueModel"]:
        """
        Retrieves an AnalyticQSASTIssue by its ID from the database.

        Args:
            issue_id (int): The unique identifier of the issue to retrieve.

        Returns:
            Optional[AnalyticQSASTIssueModel]: The found issue model if exists, None otherwise.

        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            issue = await session.get(AnalyticQSASTIssue, issue_id)
            if issue:
                return AnalyticQSASTIssueModel.model_validate(issue)
            return None

    async def add_issue(self, issue_data: "AnalyticQSASTIssueModel") -> AnalyticQSASTIssueModel:
        """
        Adds a new SAST issue to the database.
        Args:
            issue_data (AnalyticQSASTIssueModel): The SAST issue data to be added.
        Returns:
            AnalyticQSASTIssueModel: The created SAST issue model with database data.
        Raises:
            ValueError: If the scan_id is missing or None in the issue_data.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            data = issue_data.model_dump()

            if "scan_id" not in data or data["scan_id"] is None:
                raise ValueError("scan_id is required for AnalyticQSASTIssue")

            stmt = insert(AnalyticQSASTIssue).values(issue_data.model_dump()).returning(AnalyticQSASTIssue)
            result = await session.execute(stmt)

            created_issue = result.scalar_one()
            return AnalyticQSASTIssueModel.model_validate(created_issue)

    async def add_multiple_issues(self, issue_data: List[AnalyticQSASTIssueModel]) -> List[AnalyticQSASTIssueModel]:
        """
        Adds multiple SAST issues to the database.

        This method takes a list of AnalyticQSASTIssueModel objects and inserts them into the database.
        Each issue must have a scan_id associated with it.

        Args:
            issue_data (List[AnalyticQSASTIssueModel]): A list of SAST issue models to be added to the database.

        Returns:
            List[AnalyticQSASTIssueModel]: A list of the created SAST issue models with their database IDs.

        Raises:
            ValueError: If any issue in the input list lacks a scan_id.
        """
        if any("scan_id" not in issue.model_dump() or issue.scan_id is None for issue in issue_data):
            raise ValueError("Each issue must have a scan_id")

        async with AnalyticQDatabaseManager().get_db_session() as session:
            issue_list = [issue.model_dump() for issue in issue_data]
            stmt = insert(AnalyticQSASTIssue).values(issue_list).returning(AnalyticQSASTIssue)
            result = await session.execute(stmt)
            created_issues = result.scalars().all()
            return [AnalyticQSASTIssueModel.model_validate(issue) for issue in created_issues]

    async def update_issue_by_id(self, issue_id: int, issue_data: AnalyticQSASTIssueModel) -> AnalyticQSASTIssueModel:
        """
        Updates a SAST issue in the database by its ID.
        Args:
            issue_id (int): The ID of the issue to update.
            **kwargs: Arbitrary keyword arguments containing the fields to update.
        Returns:
            AnalyticQSASTIssueModel: The updated issue model.
        Raises:
            sqlalchemy.exc.NoResultFound: If no issue is found with the given ID.
            sqlalchemy.exc.MultipleResultsFound: If multiple issues are found with the given ID.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            data = issue_data.model_dump()
            if "id" in data:
                del data["id"]
            stmt = update(AnalyticQSASTIssue).where(AnalyticQSASTIssue.id == issue_id).values(data).returning(AnalyticQSASTIssue)
            result = await session.execute(stmt)

            updated_issue = result.scalar_one()
            return AnalyticQSASTIssueModel.model_validate(updated_issue)

    async def delete_issue_by_id(self, issue_id: int) -> bool:
        """
        Delete an issue from the database by its ID.

        Args:
            issue_id (int): The unique identifier of the issue to delete.

        Returns:
            bool: True if the issue was successfully deleted, False if no issue was found with the given ID.

        Raises:
            SQLAlchemyError: If there is an error executing the database operation.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = delete(AnalyticQSASTIssue).where(AnalyticQSASTIssue.id == issue_id)
            result = await session.execute(stmt)
            return result.rowcount > 0

    async def filter_scan_issues(
            self,
            scan_id: int,
            severity: Optional[str] = None,
            confidence: Optional[str] = None
    ) -> List[AnalyticQSASTIssueModel]:

        async with AnalyticQDatabaseManager().get_db_session() as session:
            # Base query
            query = select(AnalyticQSASTIssue).where(AnalyticQSASTIssue.scan_id == scan_id)

            filters = []
            # Apply severity and confidence filters
            if severity:
                filters.append(AnalyticQSASTIssue.severity == severity)
            if confidence:
                filters.append(AnalyticQSASTIssue.confidence == confidence)

            if filters:
                query = query.where(and_(*filters))

            result = await session.execute(query)
            issues = result.scalars().all()
            return [AnalyticQSASTIssueModel.model_validate(issue) for issue in issues]
