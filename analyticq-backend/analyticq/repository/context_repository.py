from typing import List, Optional

from analyticq.manager import AnalyticQDatabaseManager
from analyticq.model.scan_context import AnalyticQContext
from analyticq.repository.scan_repository import (
    AnalyticQSASTScanResult, AnalyticQSASTScanResultModel,
    AnalyticQScanResultRepository)
from analyticq.validator.context import AnalyticQContextModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import selectinload


class AnalyticQContextRepository:

    def __init__(self):
        self.scan_repo = AnalyticQScanResultRepository()

    async def get_all_contexts(self) -> List[AnalyticQContextModel]:
        """
        Retrieves all contexts from the database without pagination.

        Returns:
            List[AnalyticQContextModel]: A list of all context models in the database.

        Example:
            contexts = await context_repository.get_all_contexts()
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQContext)
            result = await session.execute(stmt)
            contexts = result.scalars().all()
            return [AnalyticQContextModel.model_validate(context) for context in contexts]

    async def get_contexts_paginated(self, page: int, page_size: int) -> tuple[List[AnalyticQContextModel], int]:
        """
        Retrieves contexts from the database with pagination.

        Args:
            page (int): The page number (1-indexed)
            page_size (int): The number of items per page

        Returns:
            tuple[List[AnalyticQContextModel], int]: A tuple containing:
                - List of context models for the requested page
            -    Total count of all contexts

        Example:
        contexts, total = await context_repository.get_contexts_paginated(1, 10)
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            # Get total count
            count_stmt = select(AnalyticQDatabaseManager.func.count()).select_from(AnalyticQContext)
            count_result = await session.execute(count_stmt)
            total_count = count_result.scalar_one()

            # Get paginated results
            offset = (page - 1) * page_size
            stmt = select(AnalyticQContext).offset(offset).limit(page_size)
            result = await session.execute(stmt)
            contexts = result.scalars().all()

            return [AnalyticQContextModel.model_validate(context) for context in contexts], total_count

    async def get_by_id(self, scan_id: int) -> Optional["AnalyticQContextModel"]:
        """
        Retrieves a context by its scan ID from the database.

        Args:
            scan_id (int): The ID of the scan context to retrieve.

        Returns:
            Optional[AnalyticQContextModel]: The context model if found, None otherwise.

        Example:
            context = await context_repository.get_by_id(123)
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            scan_context = await session.get(AnalyticQContext, scan_id)
            if scan_context:
                return AnalyticQContextModel.model_validate(scan_context)

    async def get_by_repo_name(self, repo_name: str) -> Optional["AnalyticQContextModel"]:
        """
        Retrieve a context by repository name from the database.

        Args:
            repo_name (str): The name of the repository to search for.

        Returns:
            Optional[AnalyticQContextModel]: The context model if found, None otherwise.

        Examples:
            context = await context_repository.get_by_repo_name("my-repo")
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQContext).where(AnalyticQContext.repo_name == repo_name)
            result = await session.execute(stmt)
            scan_context = result.scalars().first()
            if scan_context:
                return AnalyticQContextModel.model_validate(scan_context)

    async def get_scans_by_repo_name(self, repo_name: str) -> List[AnalyticQSASTScanResultModel]:
        """
        Retrieves all SAST scan results associated with a specific repository name.

        Args:
            repo_name (str): The name of the repository to fetch scans for.

        Returns:
            List[AnalyticQSASTScanResultModel]: A list of SAST scan result models associated with the repository.
            Returns an empty list if no context is found for the given repository name.

        Note:
            This method eagerly loads the issues related to each scan result.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            # Fetch the context by repo_name
            stmt = select(AnalyticQContext).where(AnalyticQContext.repo_name == repo_name)
            result = await session.execute(stmt)
            context = result.scalars().first()
            if not context:
                return []
            # Fetch all scans associated with the context ID
            stmt = (
                select(AnalyticQSASTScanResult)
                .where(AnalyticQSASTScanResult.context_id == context.id)
                .options(selectinload(AnalyticQSASTScanResult.issues))  # Eagerly load issues
            )

            result = await session.execute(stmt)
            scans = result.scalars().all()
            return [AnalyticQSASTScanResultModel.model_validate(scan) for scan in scans]

    async def add(self, context_data: "AnalyticQContextModel") -> AnalyticQContextModel:
        """
        Adds a new context to the database.

        This method inserts a new AnalyticQContext record using the provided context data.

        Args:
            context_data (AnalyticQContextModel): The context data model to be added to the database.

        Returns:
            AnalyticQContextModel: The newly created context model with updated information from the database.

        Raises:
            SQLAlchemyError: If there is an error during database operation.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = insert(AnalyticQContext).values(context_data.model_dump()).returning(AnalyticQContext)
            result = await session.execute(stmt)
            new_context = result.scalar_one()
            return AnalyticQContextModel.model_validate(new_context)

    async def update_by_repo_name(self, repo_name: str, **kwargs) -> AnalyticQContextModel:
        """
        Updates an AnalyticQContext record by repository name and returns the updated context.
        Args:
            repo_name (str): The name of the repository to update
            **kwargs: Arbitrary keyword arguments containing fields to update
        Returns:
            AnalyticQContextModel: The updated context model
        Raises:
            NoResultFound: If no context is found with the given repo_name
            MultipleResultsFound: If multiple contexts are found with the given repo_name
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = update(AnalyticQContext).where(AnalyticQContext.repo_name == repo_name).values(**kwargs).returning(AnalyticQContext)
            result = await session.execute(stmt)

            updated_context = result.scalar_one()
            return AnalyticQContextModel.model_validate(updated_context)

    async def delete_by_repo_name(self, repo_name: str) -> bool:
        """
        Deletes all contexts associated with a specific repository name from the database.

        Args:
            repo_name (str): The name of the repository whose contexts should be deleted.

        Returns:
            bool

        Raises:
            SQLAlchemyError: If there's an error during database operation.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = delete(AnalyticQContext).where(AnalyticQContext.repo_name == repo_name)
            result = await session.execute(stmt)
            return result.rowcount > 0
