from __future__ import annotations

from typing import List, Optional

from analyticq.engine import AnalyticQSASTScanResultModel
from analyticq.manager import AnalyticQDatabaseManager
from analyticq.model.issue import AnalyticQSASTIssue
from analyticq.model.scan_result import AnalyticQSASTScanResult
from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload


class AnalyticQScanResultRepository:
    """""
     A repository class for managing SAST scan results in the AnalyticQ system.
    This class provides methods to perform CRUD operations on scan results in the database.
    It handles both scan results and their associated issues.
    Note:
        All methods are asynchronous and should be called with await.
    """

    async def get_all_scans(self) -> List[AnalyticQSASTScanResultModel]:
        """
        Retrieves all SAST scan results from the database.

        This asynchronous method fetches all scan records including their associated issues
        using eager loading through the selectinload option.

        Returns:
            List[AnalyticQSASTScanResultModel]: A list of scan result models containing all scans
            and their related issues from the database.

        Example:
            scans = await scan_repository.get_all_scans()
            for scan in scans:
                print(scan.id, len(scan.issues))
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQSASTScanResult).options(
                selectinload(AnalyticQSASTScanResult.issues)
            )
            result = await session.execute(stmt)
            scans = result.scalars().all()
            return [AnalyticQSASTScanResultModel.model_validate(scan) for scan in scans]

    async def get_all_scans_paginated(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[AnalyticQSASTScanResultModel]:

        async with AnalyticQDatabaseManager().get_db_session() as session:
            count_stmt = select(func.count())
            count_result = await session.execute(count_stmt)
            total_count = count_result.scalar_one()

            query = select(AnalyticQSASTScanResult).options(
                selectinload(AnalyticQSASTScanResult.issues)
            ).offset(offset).limit(limit)
            result = await session.execute(query)
            scans = result.scalars().all()
            return [AnalyticQSASTScanResultModel.model_validate(scan) for scan in scans], total_count

    async def add_scan(self, scan_result_data: "AnalyticQSASTScanResultModel") -> AnalyticQSASTScanResultModel:
        """
        Adds a new SAST scan result to the database.
        Args:
            scan_result_data (AnalyticQSASTScanResultModel): The scan result data to be added.
        Returns:
            AnalyticQSASTScanResultModel: The newly created scan result model.
        Raises:
            SQLAlchemyError: If there is an error executing the database operation.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            data_dict = scan_result_data.model_dump(exclude={"issues", "context"})

            # Create the SQLAlchemy ORM object directly instead of using raw insert
            new_scan_result = AnalyticQSASTScanResult(**data_dict)
            session.add(new_scan_result)
            await session.flush()

            if hasattr(scan_result_data, 'issues') and scan_result_data.issues:
                for issue_data in scan_result_data.issues:
                    issue_dict = issue_data.model_dump(exclude={"scan_result"})

                    # Ensure scan_id is not an empty string
                    if 'scan_id' in issue_dict and not issue_dict['scan_id']:
                        del issue_dict['scan_id']

                    new_issue = AnalyticQSASTIssue(**issue_dict, scan_id=new_scan_result.id)
                    session.add(new_issue)

            # Load the result with relationships explicitly
            result = await session.execute(
                select(AnalyticQSASTScanResult)
                .options(selectinload(AnalyticQSASTScanResult.issues))
                .where(AnalyticQSASTScanResult.id == new_scan_result.id)
            )
            created_scan_result = result.scalar_one()

            return AnalyticQSASTScanResultModel.model_validate(created_scan_result)

    async def get_by_scan_id(self, id: int) -> Optional["AnalyticQSASTScanResultModel"]:
        """
        Retrieves a SAST scan result by its scan ID.
        This method queries the database for a scan result with the specified scan ID,
        including eagerly loaded related issues.
        Args:
            id (str): The unique identifier of the scan to retrieve.
        Returns:
            Optional[AnalyticQSASTScanResultModel]: The scan result model if found, None otherwise.
        Example:
            scan_result = await scan_repository.get_by_scan_id("scan_123")
                print(f"Found scan with {len(scan_result.issues)} issues")
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = (
                select(AnalyticQSASTScanResult)
                .where(AnalyticQSASTScanResult.id == id)
                .options(selectinload(AnalyticQSASTScanResult.issues))  # Eagerly load issues
            )
            result = await session.execute(stmt)
            scan_result = result.scalars().first()
            if scan_result:
                return AnalyticQSASTScanResultModel.model_validate(scan_result)
        return None

    async def get_by_scan_id_str(self, scan_id: str) -> Optional[AnalyticQSASTScanResultModel]:
        """
        Retrieves a SAST scan result from the database by its scan ID.

        Args:
            scan_id (str): The unique identifier of the scan to retrieve.

        Returns:
            Optional[AnalyticQSASTScanResultModel]: The scan result model if found, None otherwise.
                The returned model includes eagerly loaded issues.

        Example:
            scan_result = await scan_repository.get_by_scan_id("scan123")
                print(f"Found scan with {len(scan_result.issues)} issues")
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = (
                select(AnalyticQSASTScanResult)
                .where(AnalyticQSASTScanResult.scan_id == scan_id)
                .options(selectinload(AnalyticQSASTScanResult.issues))  # Eagerly load issues
            )
            result = await session.execute(stmt)
            scan_result = result.scalars().first()
            if scan_result:
                return AnalyticQSASTScanResultModel.model_validate(scan_result)
        return None

    async def get_scans_by_tool_name(self, tool_name: str) -> List[AnalyticQSASTScanResultModel]:
        """
        Asynchronously retrieves all SAST scan results for a specific tool from the database.

        Args:
            tool_name (str): The name of the SAST tool to filter scan results by.

        Returns:
            List[AnalyticQSASTScanResultModel]: A list of scan result objects matching the tool name.

        Example:
            scans = await repo.get_scans_by_tool_name("Bandit")
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = select(AnalyticQSASTScanResult).where(
                AnalyticQSASTScanResult.tool_name == tool_name
            ).options(selectinload(AnalyticQSASTScanResult.issues))
            result = await session.execute(stmt)
            scans = result.scalars().all()
            return [AnalyticQSASTScanResultModel.model_validate(scan) for scan in scans]

    async def update_scan_by_id(self, id: int, scan_data: AnalyticQSASTScanResultModel) -> AnalyticQSASTScanResultModel:
        """
        Updates a scan result record in the database based on the provided scan_id.
        Args:
            scan_id (str): The unique identifier of the scan to update
            **kwargs: Variable keyword arguments containing fields to update
        Returns:
            AnalyticQSASTScanResultModel: The updated scan result model
        Raises:
            SQLAlchemyError: If there is a database error during the update operation
        """

        async with AnalyticQDatabaseManager().get_db_session() as session:
            # First, retrieve the existing record
            stmt = select(AnalyticQSASTScanResult).where(AnalyticQSASTScanResult.id == id)
            result = await session.execute(stmt)
            existing_scan = result.scalar_one_or_none()

            if not existing_scan:
                raise ValueError(f"Scan with scan_id {id} not found")

            data_dict = scan_data.model_dump(exclude={"issues", "context", "id"})

            for key, value in data_dict.items():
                if hasattr(existing_scan, key):
                    setattr(existing_scan, key, value)

            # Handle issues update if needed
            if hasattr(scan_data, 'issues') and scan_data.issues:
                # First delete existing issues
                delete_stmt = delete(AnalyticQSASTIssue).where(AnalyticQSASTIssue.scan_id == id)
                await session.execute(delete_stmt)

                # Then add the new ones
                for issue_data in scan_data.issues:
                    issue_dict = issue_data.model_dump(exclude={"scan_result"})
                    new_issue = AnalyticQSASTIssue(**issue_dict, scan_id=id)
                    session.add(new_issue)

            await session.flush()

            # Load the updated result with relationships
            result = await session.execute(
                select(AnalyticQSASTScanResult)
                .options(selectinload(AnalyticQSASTScanResult.issues))
                .where(AnalyticQSASTScanResult.id == id)
            )
            updated_scan_result = result.scalar_one()
            return AnalyticQSASTScanResultModel.model_validate(updated_scan_result)

    async def delete_scan_by_id(self, id: int) -> bool:
        """
        Deletes SAST scan results from the database based on the provided scan ID.

        Args:
            scan_id (int): The unique identifier of the scan to be deleted.

        Returns:
            bool: True if at least one record was deleted, False otherwise.

        Raises:
            SQLAlchemyError: If there is an error executing the database operation.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = delete(AnalyticQSASTScanResult).where(AnalyticQSASTScanResult.id == id)
            result = await session.execute(stmt)
            return result.rowcount > 0
