from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class ESLintParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "ruleId",
            "message": "message",
            "path": "filePath",
            "start_line": "line",
            "end_line": "endLine",
            "column": "column",
            "end_column": "endColumn",
            "severity": "severity",
            "node_type": "nodeType",
            "code": "source",
            "metadata": "metadata"
        }
        super().__init__(tool_name="eslint", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        # ESLint doesn't provide confidence levels, so we use a default
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level):
        # ESLint uses numeric severity levels: 0=off, 1=warning, 2=error
        severity_map = {
            0: AnalyticQSeverity.INFO,
            1: AnalyticQSeverity.MEDIUM,
            2: AnalyticQSeverity.HIGH
        }

        # Convert string to int if needed
        if isinstance(severity_level, str) and severity_level.isdigit():
            severity_level = int(severity_level)

        return severity_map.get(severity_level, AnalyticQSeverity.UNKNOWN)

    def transform_output(self, raw_result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed_issues = []

        for file_data in raw_result:
            file_path = file_data.get("filePath", "unknown")
            source_code = file_data.get("source", "")

            for message in file_data.get("messages", []):
                transformed_issue = {
                    "ruleId": message.get("ruleId", "unknown"),
                    "filePath": file_path,
                    "message": message.get("message", "unknown"),
                    "severity": message.get("severity", 0),
                    "line": message.get("line", 0),
                    "endLine": message.get("endLine", message.get("line", 0)),
                    "column": message.get("column", 0),
                    "endColumn": message.get("endColumn", message.get("column", 0)),
                    "nodeType": message.get("nodeType", "unknown"),
                    "source": source_code
                }

                # Add any suggestions as metadata
                if "suggestions" in message:
                    transformed_issue["metadata"] = {
                        "suggestions": message.get("suggestions", [])
                    }

                transformed_issues.append(transformed_issue)

        return transformed_issues

    def parse_scan_result(self, raw_result) -> AnalyticQSASTScanResult:
        try:
            transformed_results = self.transform_output(raw_result)

            # Use base class's parse_scan_result
            scan_result = super().parse_scan_result(transformed_results)

            # Add ESLint-specific metadata
            total_errors = 0
            total_warnings = 0

            for file_data in raw_result:
                total_errors += file_data.get("errorCount", 0)
                total_warnings += file_data.get("warningCount", 0)

            scan_result.metadata.update({
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "total_fixable_errors": sum(file_data.get("fixableErrorCount", 0) for file_data in raw_result),
                "total_fixable_warnings": sum(file_data.get("fixableWarningCount", 0) for file_data in raw_result)
            })

            scan_result.summary.update({
                "error_count": total_errors,
                "warning_count": total_warnings,
                "files_analyzed": len(raw_result)
            })

            return scan_result

        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing ESLint results: {str(e)}"
            )
