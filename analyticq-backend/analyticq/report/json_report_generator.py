from typing import Any, Dict

from .report_generator import ReportGenerator


class JSONReportGenerator(ReportGenerator):
    """Generate JSON report."""

    def generate(self) -> Dict[str, Any]:
        base_data = self.get_base_data()

        # Format issues for JSON
        formatted_issues = []
        for issue in self.scan_result.issues:
            formatted_issues.append(self.get_issue_data(issue))

        report_data = {
            **base_data,
            "issues": formatted_issues,
            "report_generated_at": self.timestamp.isoformat()
        }

        # Remove complex objects that can't be serialized
        if "created_at" in report_data:
            report_data["created_at"] = report_data["created_at"].isoformat() if report_data["created_at"] else None
        if "updated_at" in report_data:
            report_data["updated_at"] = report_data["updated_at"].isoformat() if report_data["updated_at"] else None

        return report_data
