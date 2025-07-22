
import logging

from analyticq.report.report_manager import ReportManager
from analyticq.repository.scan_repository import AnalyticQScanResultRepository
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AnalyticQReportService:

    def __init__(self, scan_repo: AnalyticQScanResultRepository):
        self.scan_repo = scan_repo

    async def get_scan_report(self, scan_id: str, format_type: str):
        """
        Retrieves and generates a scan report in the specified format.

        Args:
            scan_id (str): The unique identifier of the scan to generate the report for
            format_type (str): The desired format type for the report

        Returns:
            The generated report in the specified format

        Raises:
            HTTPException: If scan is not found (404) or if there's an error generating the report (500)
        """
        try:
            scan = await self.scan_repo.get_by_scan_id_str(scan_id)
            if not scan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with ID {scan_id} not found."
                )
            return ReportManager.generate_report(scan_result=scan, format_type=format_type)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting report in the format requested {format_type}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"EError getting report in the format requested {format_type}: {str(e)}"
            )

    async def get_reports_by_tool(self, tool_name: str, format_type):
        try:
            scans = await self.scan_repo.get_scans_by_tool_name(tool_name)
            if not scans:
                return []

            if format_type:
                reports = []
                for scan in scans:
                    report = ReportManager.generate_report(scan_result=scan, format_type=format_type)
                    reports.append({
                        "scan_id": scan.scan_id,
                        "report": report
                    })
                return reports

            return scans

        except Exception as e:
            logger.error(f"Error getting reports by tool {tool_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting reports by tool {tool_name}: {str(e)}"
            )

    async def get_codebase_name_by_scan(self, id: int) -> str:
        try:
            codebase_name = await self.scan_repo.get_codebase_name_from_scan(id)
            if not codebase_name:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with ID {id} not found."
                )
            return codebase_name
        except Exception as e:
            logger.error(f"Error retrieving codebase name for scan {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving codebase name for scan {id}: {str(e)}"
            )
