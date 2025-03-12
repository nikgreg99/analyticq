from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class BearerParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "id",
            "message": "title",
            "code": "code_extract",
            "path": "full_filename",
            "start_line": "line_number",
            "endl_line": "line_number",
            "column": "column_info.start",
            "severity": "severity_level",
            "issue_metadata": "metadata"
        }
        super().__init__(tool_name="bearer", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        if not severity_level or not isinstance(severity_level, str):
            return AnalyticQSeverity.UNKNOWN
        # Bearer categorizes findings by severity levels: critical, high, medium, low, info
        try:
            return AnalyticQSeverity.parse(severity_level)
        except ValueError as e:
            raise e

    def transform_output(self, raw_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        transformed_issues = []

        # Process each severity level (critical, high, medium, low, info)
        for severity_level, issues in raw_result.items():
            if not isinstance(issues, list):
                continue

            for issue in issues:
                column_info = {}
                # Extract location issue
                if "source" in issue and "column" in issue["source"]:
                    column_info = {
                        "start": issue["source"]["column"].get("start", 0),
                        "end": issue["source"]["column"].get("end", 0)
                    }

                transformed_issue = {
                    "id": issue.get("id", "unknown"),
                    "title": issue.get("title", "unknown"),
                    "severity_level": severity_level,
                    "full_filename": issue.get("full_filename", "unknown"),
                    "line_number": issue.get("line_number", "unknown"),
                    "code_extract": issue.get("code_extract", "unknown"),
                    "column": column_info,
                    "metadata" : {
                        "description": issue.get("description", ""),
                        "cwe_ids": issue.get("cwe_ids", []),
                        "fingerprint": issue.get("fingerprint", ""),
                    }
                }

                transformed_issues.append(transformed_issue)

        return transformed_issues

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        try:
            transformed_results = self.transform_output(raw_result)
            scan_result = super().parse_scan_result(transformed_results)

            scan_result.scan_metadata.update({
                "total_critical": len(raw_result.get("critical", [])),
                "total_high": len(raw_result.get("high", [])),
                "total_medium": len(raw_result.get("medium", [])),
                "total_low": len(raw_result.get("low", [])),
                "total_info": len(raw_result.get("info", []))
            })

            return scan_result

        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing Bearer results: {str(e)}"
            ) from e
