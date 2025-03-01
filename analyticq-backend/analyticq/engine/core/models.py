from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalyticQConfidence(Enum):
    """
    Enumeration representing confidence levels in AnalyticQ analysis results.

    Attributes:
        HIGH (str): Highest level of confidence
        MEDIUM (str): Moderate level of confidence
        LOW (str): Low level of confidence
        UNKNOWN (str): Confidence level cannot be determined
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    CRITICAL = "CRIICAL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def parse(cls, confidence_str: str):
        try:
            return cls[confidence_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid confidence level: {confidence_str}")


class AnalyticQSeverity(Enum):
    """
    Enumeration representing severity levels for AnalyticQ issues.

    Attributes:
        HIGH (str): Critical severity level
        MEDIUM (str): Moderate severity level
        LOW (str): Minor severity level
        UNKNOWN (str): Undefined severity level
    """
    INFO = "INFO"  # Not all SAST tool support this severity level
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def parse(cls, severity_str: str):
        try:
            return cls[severity_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid severity level: {severity_str}")


class AnalyticQScanContext(BaseModel):
    """
    Context class for storing repository scan-related information.

    Attributes:
        repo_name (str): Repository name being scanned
        branch (Optional[str]): Branch being scanned
        last_commit_hash (Optional[str]): Hash of the last commit in scan
    """
    repo_name: str
    branch: Optional[str] = None
    last_commit_hash: Optional[str] = None


class AnalyticQSASTIssue(BaseModel):
    rule_id: str
    severity: AnalyticQSeverity
    confidence: AnalyticQConfidence
    code: str = Field(default="Not present")
    message: str = Field(default="No message")
    path: str = Field(default="unknown")
    start_line: int = Field(default=0, ge=0)
    end_line: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default=None)


class AnalyticQSASTScanResult(BaseModel):
    """
    Contains results of a SAST scan in AnalyticQ.

    Attributes:
        scan_id (str): Unique identifier for the scan
        context (AnalyticQScanContext): Scan execution context
        issues (List[AnalyticQSASTIssue]): List of discovered security issues
        summary (Dict[str, Any]): Aggregated scan statistics
        metadata (Dict[str, Any]): Additional scan metadata
    """
    scan_id: str
    context: Optional[AnalyticQScanContext] = None
    issues: List[AnalyticQSASTIssue]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]
