import io
import json
from datetime import datetime
from typing import Literal

from analyticq.service.scan_service import (AnalyticQScanResultRepository,
                                            AnalyticQScanService)
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import HTMLResponse, StreamingResponse

report_router = APIRouter(prefix="/reports", tags=["reports"])


def get_scan_service(
    repo: AnalyticQScanResultRepository = Depends(AnalyticQScanResultRepository)
) -> AnalyticQScanService:
    """Dependency provider for scan service."""
    return AnalyticQScanService(repo)


@report_router.get("/download/{scan_id}")
async def download_report(
    scan_id: str,
    format: Literal["pdf", "json", "html", "csv"] = Query(..., description="Report format: pdf, json, html, or csv"),
    scan_service: AnalyticQScanService = Depends(get_scan_service)
):
    content = await scan_service.get_scan_report(scan_id, format)
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
