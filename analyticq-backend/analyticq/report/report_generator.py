from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from analyticq.validator.scan import AnalyticQSASTScanResultModel


class ReportGenerator(ABC):
    """Abstract base class for report generators."""

    def __init__(self, scan_result: AnalyticQSASTScanResultModel):
        self.scan_result = scan_result
        self.timestamp = datetime.now()

    @abstractmethod
    def generate(self) -> Any:
        """Generate the report in the specific format."""
        pass

    def get_base_data(self) -> Dict[str, Any]:
        """Get common data for all report types."""
        issues_summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0,
            "UNKNOWN": 0
        }

        for issue in self.scan_result.issues:
            severity = getattr(issue.severity, "value", str(issue.severity)).upper()
            if severity in issues_summary:
                issues_summary[severity] += 1
            else:
                issues_summary["UNKNOWN"] += 1

        return {
            "scan_id": self.scan_result.scan_id,
            "tool_name": self.scan_result.tool_name,
            "created_at": self.scan_result.created_at,
            "updated_at": self.scan_result.updated_at,
            "summary": self.scan_result.summary,
            "scan_metadata": self.scan_result.scan_metadata,
            "issues": self.scan_result.issues,
            "issues_summary": issues_summary,
            "total_issues": len(self.scan_result.issues),
            "report_generated_at": self.timestamp
        }

    def get_issue_data(self, issue) -> Dict[str, Any]:
        """Extract data from an issue object."""
        return {
            "id": issue.id,
            "rule_id": issue.rule_id,
            "severity": getattr(issue.severity, "value", str(issue.severity)),
            "confidence": getattr(issue.confidence, "value", str(issue.confidence)),
            "message": issue.message,
            "path": issue.path,
            "start_line": issue.start_line,
            "end_line": issue.end_line,
            "column": issue.column,
            "code": issue.code,
            "issue_metadata": issue.issue_metadata,
            "summary": issue.summary
        }
