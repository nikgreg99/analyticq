import io
import json
from datetime import datetime
from typing import Literal, Optional

from analyticq.service.report_service import AnalyticQReportService
from analyticq.service.scan_service import AnalyticQScanResultRepository
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import HTMLResponse, StreamingResponse

report_router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service(
    repo: AnalyticQScanResultRepository = Depends(AnalyticQScanResultRepository)
) -> AnalyticQReportService:
    """Dependency provider for scan service."""
    return AnalyticQReportService(repo)


@report_router.get("/download/{scan_id}")
async def download_report(
    scan_id: str,
    format: Literal["pdf", "json", "html", "csv"] = Query(..., description="Report format: pdf, json, html, or csv"),
    report_service: AnalyticQReportService = Depends(get_report_service)
):
    content = await report_service.get_scan_report(scan_id, format)
    report_filename = f"analyticq_report_{scan_id}_{datetime.now().strftime('%Y%m%d')}".lower()

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
