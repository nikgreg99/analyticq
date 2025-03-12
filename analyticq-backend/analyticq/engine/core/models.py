from enum import Enum
from typing import Any, Dict, List

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


class AnalyticQSASTIssueModel(BaseModel):
    """
    A model representing a Security Analysis Static Testing (SAST) issue detected by AnalyticQ.

    This class inherits from BaseModel and defines the structure of a security issue
    found during static code analysis.

    Attributes:
        rule_id (str): Unique identifier of the rule that detected the issue.
        severity (AnalyticQSeverity): The severity level of the detected issue.
        confidence (AnalyticQConfidence): The confidence level of the detection.
        code (str): The problematic code snippet. Defaults to "Not present".
        message (str): Description of the issue. Defaults to "No message".
        path (str): File path where the issue was found. Defaults to "unknown".
        start_line (int): Starting line number of the issue in the file. Must be >= 0.
        end_line (int): Ending line number of the issue in the file. Must be >= 0.
        metadata (Dict[str, Any]): Additional information about the issue. Defaults to None.
    """
    rule_id: str
    severity: AnalyticQSeverity
    confidence: AnalyticQConfidence
    code: str = Field(default="Not present")
    message: str = Field(default="No message")
    path: str = Field(default="unknown")
    start_line: int = Field(default=0, ge=0)
    end_line: int = Field(default=0, ge=0)
    column: int = Field(default=0, ge=0)
    issue_metadata: Dict[str, Any] = Field(default=None)

    class Config:
        from_attributes = True


class AnalyticQSASTScanResultModel(BaseModel):
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
    issues: List[AnalyticQSASTIssueModel] = []
    summary: Dict[str, Any]
    scan_metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True
