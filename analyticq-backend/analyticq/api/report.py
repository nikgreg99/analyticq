import io
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from analyticq.service.report_service import AnalyticQReportService
from analyticq.service.scan_service import AnalyticQScanResultRepository
from analyticq.util import PathUtil
from fastapi import APIRouter, Depends, Query, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

logger = logging.getLogger(__name__)

report_router = APIRouter(prefix="/reports", tags=["reports"])

REPORT_FOLDER = PathUtil.get_codebase_report_AnalyticQ_path()

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "json": "application/json",
    "html": "text/html",
    "csv": "text/csv"
}


def get_report_service(
    repo: AnalyticQScanResultRepository = Depends(AnalyticQScanResultRepository)
) -> AnalyticQReportService:
    """Dependency provider for scan service."""
    return AnalyticQReportService(repo)


def get_report_filename(scan_id: str, codebase_name: str, format: str, include_date: bool = True) -> str:
    """
    Generate a filename for a report based on scan ID and format.

    Parameters:
        scan_id (str): The unique identifier of the scan
        format (str): The desired file format for the report (e.g., 'PDF', 'CSV')
        include_date (bool, optional): Whether to include current date in filename. Defaults to True.

    Returns:
        str: The generated filename in the format 'analyticq_report_{scan_id}_{date}.{format}'
             or 'analyticq_report_{scan_id}.{format}' if include_date is False

    """

    if include_date:
        return f"{codebase_name}_{scan_id}_{datetime.now().strftime('%Y%m%d')}.{format.lower()}"
    else:
        return f"{codebase_name}_{scan_id}.{format.lower()}"


def get_report_filepath(scan_id: str, codebase_name: str, format: str, include_date: bool = True) -> Path:
    """
    Generate a file path for a report based on scan ID and format.

    Parameters:
        scan_id (str): The unique identifier of the scan
        format (str): The desired file format for the report (e.g., 'PDF', 'CSV')
        include_date (bool, optional): Whether to include current date in filename. Defaults to True.

    """
    filename = get_report_filename(scan_id, codebase_name, format, include_date)
    return REPORT_FOLDER / filename


async def save_report_to_file(content, codebase_name: str, scan_id: str, format: str, include_date: bool = True) -> Path:
    """Save report content to a file with specified format.

    This async function saves report content to a file in the specified format (json, html, csv, or pdf).
    The file path is determined by the scan_id and format parameters.

    Args:
        content (Union[dict, str, bytes, BytesIO]): The content to save. Can be:
            - dict or JSON-serializable object for json format
            - string for html/csv format
            - bytes or BytesIO object for pdf format
        scan_id (str): Unique identifier for the scan
        format (str): Output format - one of: "json", "html", "csv", "pdf"
        include_date (bool, optional): Whether to include date in filename. Defaults to True.

    Returns:
        Path: Path object pointing to the saved file

    Raises:
        ValueError: If content type doesn't match the specified format
    """
    filepath = get_report_filepath(scan_id, codebase_name, format, include_date)

    if format == "json":
        with open(filepath, "w", encoding="utf-8") as f:
            if isinstance(content, dict):
                f.write(str(content))
            else:
                json.dump(content, f, indent=2)
    elif format in ["html", "csv"]:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    elif format == "pdf":
        with open(filepath, 'wb') as f:
            if isinstance(content, bytes):
                f.write(content)
            else:
                f.write(content.getvalue())

    return filepath


def find_existing_report(scan_id: str, codebase_name: str, format: str) -> Optional[Path]:
    """
    Check if a report file already exists for the given scan ID and format.

    Parameters:
        scan_id (str): The unique identifier of the scan
        format (str): The desired file format for the report (e.g., 'PDF', 'CSV')

    Returns:
        Optional[Path]: The path to the existing report file if found, otherwise None
    """
    filepath_with_date = get_report_filepath(scan_id, codebase_name, format, include_date=True)
    if filepath_with_date.exists():
        return filepath_with_date

    filepath_without_date = get_report_filepath(scan_id, codebase_name, format, include_date=False)
    if filepath_without_date.exists():
        return filepath_without_date

    pattern = f"{codebase_name}_{scan_id}_*.{format}"
    matching_files = list(REPORT_FOLDER.glob(pattern))

    if matching_files:
        return max(matching_files, key=os.path.getmtime)

    return None


@report_router.get("/download/{scan_id}")
async def download_report(
    scan_id: str,
    format: Literal["pdf", "json", "html", "csv"] = Query(..., description="Report format: pdf, json, html, or csv"),
    force_regenerate: bool = Query(False, description="Force regenerate report even if it exists"),
    report_service: AnalyticQReportService = Depends(get_report_service)
):
    codebase_name = await report_service.get_codebase_name_by_scan(scan_id)
    logger.info(f"Generating report for scan_id: {scan_id}, codebase_name: {codebase_name}, format: {format}")
    if not force_regenerate:
        existing_report = find_existing_report(scan_id, codebase_name, format)
        if existing_report:
            media_types = {
                "pdf": "application/pdf",
                "json": "application/json",
                "html": "text/html",
                "csv": "text/csv"
            }

            return FileResponse(
                path=existing_report,
                media_type=media_types[format],
                filename=existing_report.name,
                headers={"Content-Disposition": f"attachment; filename={existing_report.name}"}
            )

    try:
        content = await report_service.get_scan_report(scan_id, format)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Report not found for scan_id: {scan_id}")

    try:
        await save_report_to_file(content, codebase_name, scan_id, format)
    except Exception as e:
        logger.error(f"Error saving report for scan_id {scan_id} in format {format}: {e}")

    report_filename = get_report_filename(scan_id, codebase_name, format)

    logger.debug(f"Returning report file: {report_filename} in format {format}")

    if format == "json":
        return Response(
            content=json.dumps(content, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={report_filename}.json"}
        )
    elif format == "html":
        return HTMLResponse(
            content=content,
            headers={"Content-Disposition": f"attachment; filename={report_filename}.html"}
        )
    elif format == "pdf":
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report_filename}.pdf"}
        )
    elif format == "csv":
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report_filename}.csv"}
        )


@report_router.get("/by-tool/{tool_name}")
async def get_reports_by_tool(
    tool_name: str,
    format: Optional[Literal["pdf", "json", "html", "csv"]] = Query(None, description="Optional format for the report: pdf, json, html, or csv"),
    report_service: AnalyticQReportService = Depends(get_report_service)
):
    return await report_service.get_reports_by_tool(tool_name, format)


@report_router.get("/supported-formats")
async def get_supported_formats():
    """Returns a dictionary containing the list of supported export formats.

    The function provides information about file formats that can be used for exporting reports.

    """
    return {
        "supported_formats": [
            {"format": "pdf", "description": "Portable Document Format", "media_type": "application/pdf"},
            {"format": "json", "description": "JavaScript Object Notation", "media_type": "application/json"},
            {"format": "html", "description": "HyperText Markup Language", "media_type": "text/html"},
            {"format": "csv", "description": "Comma Separated Values", "media_type": "text/csv"}
        ]
    }
