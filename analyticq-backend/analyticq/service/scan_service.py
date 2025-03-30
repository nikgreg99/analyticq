import logging
from typing import List, Optional

from analyticq.repository.scan_repository import (
    AnalyticQSASTIssueModel, AnalyticQSASTScanResultModel,
    AnalyticQScanResultRepository)
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

    async def get_scan(self, scan_id: str) -> AnalyticQSASTScanResultModel:
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
            scan = await self.scan_repo.get_by_scan_id(scan_id)
            if not scan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with {scan_id} not found"
                )
            return scan
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting scans scan {str(e)}"
            )

    async def update_scan(self, scan_id: str, updated_data: ScanUpdateRequest) -> AnalyticQSASTScanResultModel:
        """
        Updates a scan with the given ID using the provided data.

        Args:
            scan_id (str): The ID of the scan to update
            updated_data (ScanUpdateRequest): The data to update the scan with

        Returns:
            AnalyticQSASTScanResultModel: The updated scan object

        Raises:
            HTTPException: If scan is not found (404) or if there's an error updating the scan (500)
        """
        try:
            scan = await self.scan_repo.update_by_scan_id(scan_id, **updated_data.model_dump(exclude_unset=True))
            if not scan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with ID {scan_id} not found "
                )
            return scan
        except ValueError as e:
            logger.error(f"Validation error while updating scan: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error getting scan {scan_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating scan: {str(e)}"
            )

    async def filter_scan_issues(
            self,
            scan_id: str,
            severity: Optional[str] = None,
            confidence: Optional[str] = None
    ) -> List[AnalyticQSASTIssueModel]:
        try:
            issues = await self.scan_repo.get_all_issues_by_scan_id(scan_id, severity, confidence)
            return issues
        except Exception as e:
            logger.error(f"Error retrieving issues for scan {scan_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving the issues."
            )

    async def get_scans_by_tool_name(self, sast_tool: str) -> List[AnalyticQSASTScanResultModel]:
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
            scans = await self.scan_repo.get_scans_by_tool_name(sast_tool)
            return scans or []
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving scans for SAST tool {sast_tool}: {str(e)}"
            )

    async def get_issues_by_tool_name(self, tool_name: str) -> List[AnalyticQSASTIssueModel]:
        """
        Retrieve all issues found by a specific security analysis tool.
        This method fetches all scan records for a given tool name and collects all associated issues.
        Args:
            tool_name (str): The name of the security analysis tool to filter issues by.
        Returns:
            List[AnalyticQSASTIssueModel]: A list of issues found by the specified tool.
                Returns empty list if no scans are found for the tool.
        Raises:
            HTTPException: If there's an error retrieving the issues, with status code 500.
        """
        try:
            scans = await self.scan_repo.get_scans_by_tool_name(tool_name)
            if not scans:
                return []

            issues = []
            for scan in scans:
                scan_issues = await self.scan_repo.filter_scan_issues(scan.scan_id)
                issues.extend(scan_issues)
            return issues
        except Exception as e:
            logger.error(f"Unexpected error while retrieving issues for tool {tool_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error while retrieving issues for too {tool_name}: {str(e)}"
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
            deleted = await self.scan_repo.delete_by_scan_id(scan_id)
            if not deleted:
                logger.error(f"Scan with ID {scan_id} not found during deletion.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with ID {scan_id} not found."
                )
            logger.info(f"Scan deleted successfully: {scan_id}")
        except Exception as e:
            logger.error(f"Error deleting scan {scan_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting spam : {str(e)}"
            )
