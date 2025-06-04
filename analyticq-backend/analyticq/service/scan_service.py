import logging
from typing import List

from analyticq.repository.scan_repository import (
    AnalyticQSASTScanResultModel, AnalyticQScanResultRepository)
from analyticq.schemas.scan_dto import ScanCreateRequest, ScanUpdateRequest
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AnalyticQScanService:
    """
    A service class for managing SAST (Static Application Security Testing) scan operations.
    This class provides methods to create, retrieve, update and delete scan results,
    as well as filter and query scan issues based on various criteria.
   """

    def __init__(self, scan_repo: AnalyticQScanResultRepository):
        self.scan_repo = scan_repo

    async def get_all_scan(self) -> List[AnalyticQSASTScanResultModel]:
        """
        Retrieves all SAST scan results from the repository.

        Returns:
            List[AnalyticQSASTScanResultModel]: A list containing all SAST scan results.

        Raises:
            HTTPException: If there is an error retrieving the scans from the repository.
                - status_code: 500
                - detail: Error message describing the issue
        """
        try:
            scans = await self.scan_repo.get_all_scans()
            return scans
        except Exception as e:
            logger.error(f"Error getting all scan: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting all scans {str(e)}"
            )

    async def get_all_scans_paginated(self, offset: int, limit: int):
        """
        Retrieve all scans with pagination.

        This method fetches a paginated list of scans from the database along with the total count of records.

        Args:
            offset (int): Number of records to skip before starting to return rows
            limit (int): Maximum number of records to return

        Returns:
            tuple: A tuple containing:
                - list: List of scan records
                - int: Total number of scans in the database

        Raises:
            HTTPException: If the scan table is empty (404) or if there's a server error (500)
        """
        try:
            scans, total_counts = await self.scan_repo.get_all_scans_paginated(offset, limit)
            if not scans:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scan table is empty:"
                )
            return scans, total_counts
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting paginated scans: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting paginated scans: {str(e)}"
            )

    async def create_scan(self, scan_data: ScanCreateRequest) -> AnalyticQSASTScanResultModel:
        """
        Creates a new scan record in the system.

        Args:
            scan_data (ScanCreateRequest): The data required to create a new scan.

        Returns:
            AnalyticQSASTScanResultModel: The created scan object with all its details.

        Raises:
            HTTPException: If there's an error creating the scan or retrieving the created scan.
                - HTTP 500: Internal server error if the scan creation fails or cannot be retrieved.

        Example:
            scan = await scan_service.create_scan(scan_data)
        """
        try:
            scan = await self.scan_repo.add_scan(scan_data)
            if not scan:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrive created scan."
                )
            logger.info(f"Scan created successfully: {scan.scan_id}")
            return scan
        except ValueError as e:
            logger.error(f"Validation error while updating scan: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating scan: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating scan {str(e)}"
            )

    async def get_scan_by_id(self, id: int) -> AnalyticQSASTScanResultModel:
        """
        Retrieves a specific SAST scan result by its ID.

        Args:
            scan_id (str): The unique identifier of the scan to retrieve.

        Returns:
            AnalyticQSASTScanResultModel: The scan result object if found.

        Raises:
            HTTPException: If the scan is not found (404) or if there's a server error (500).
        """
        try:
            scan = await self.scan_repo.get_by_scan_id(id)
            if not scan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with {id} not found"
                )
            return scan
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting scans scan {str(e)}"
            )

    async def update_scan(self, id: int, updated_data: ScanUpdateRequest) -> AnalyticQSASTScanResultModel:
        """
        Updates a scan with the given ID using the provided data.

        Args:
            scan_id (int): The ID of the scan to update
            updated_data (ScanUpdateRequest): The data to update the scan with

        Returns:
            AnalyticQSASTScanResultModel: The updated scan object

        Raises:
            HTTPException: If scan is not found (404) or if there's an error updating the scan (500)
        """
        try:
            scan = await self.scan_repo.update_scan_by_id(id, **updated_data.model_dump(exclude_unset=True))
            if not scan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with ID {id} not found "
                )
            return scan
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"Validation error while updating scan: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error getting scan {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating scan: {str(e)}"
            )

    async def get_scans_by_tool_name(self, tool_name: str) -> List[AnalyticQSASTScanResultModel]:
        """
        Retrieve a list of scan results for a specific SAST tool.
        Args:
            sast_tool (str): The name of the SAST tool to filter scans by.
        Returns:
            List[AnalyticQSASTScanResultModel]: A list of scan result models matching the tool name.
            Returns empty list if no scans are found.
        Raises:
            HTTPException: If there is an error retrieving the scans from the repository.
                Returns 500 status code with error details.
        """
        try:
            scans = await self.scan_repo.get_scans_by_tool_name(tool_name)
            return scans or []
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving scans for SAST tool {tool_name}: {str(e)}"
            )

    async def delete_scan(self, scan_id: str) -> None:
        """
        Asynchronously deletes a scan from the repository by its ID.

        Args:
            scan_id (str): The unique identifier of the scan to delete.

        Raises:
            HTTPException: If there is an error while deleting the scan from the repository.
                Returns a 500 Internal Server Error with error details.

        Returns:
            None
        """
        try:
            deleted = await self.scan_repo.delete_scan_by_id(scan_id)
            if not deleted:
                logger.error(f"Scan with ID {scan_id} not found during deletion operation.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with ID {scan_id} not found."
                )
            logger.info(f"Scan deleted successfully: {scan_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting scan {scan_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting scan : {str(e)}"
            )
