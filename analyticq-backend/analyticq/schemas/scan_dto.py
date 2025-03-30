from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ScanCreateRequest(BaseModel):
    scan_id: str
    summary: Dict[str, Any]
    scan_metadata: Dict[str, Any] = Field(default={})


class ScanUpdateRequest(BaseModel):
    summary: Optional[Dict[str, Any]] = None
    scan_metadata: Optional[Dict[str, Any]] = None
