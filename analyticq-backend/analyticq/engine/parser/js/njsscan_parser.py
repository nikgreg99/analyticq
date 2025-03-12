from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class NjsScanParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "ruele_id": "rule_id",
            "message": "description",
            "path": "file_path",
            "start_line": "start_line",
            "end_line": "end_line",
            "column": "column",
            "code": "match_string",
            "sevevrity": "severity",
            "confidence": "confidence",
            "issue_metadata": "metadata"
        }
        super().__init__(tool_name="njsscan", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        severity_map = {
            "INFO": AnalyticQSeverity.INFO,
            "WARNING": AnalyticQSeverity.MEDIUM,
            "ERROR": AnalyticQSeverity.HIGH
        }
        return severity_map.get(severity_level, AnalyticQSeverity.UNKNOWN)

    def transform_output(self, raw_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        transformed_issues = []

        nodejs_issues = raw_result.get("nodejs", {})

        for rule_id, issue in nodejs_issues.items():
            metadata = issue.get("metadata", {})

            files = issue.get("files", [])

            if files:
                for file_data in files:
                    match_lines = file_data.get("match_lines", [0, 0])
                    match_position = file_data.get("match_position", [0, 0])

                    transformed_issue = {
                        "rule_id": rule_id,
                        "description": metadata.get("description", "unknown"),
                        "file_path": file_data.get("file_path", "unknown"),
                        "severity": metadata.get("severity", "UNKNOWN"),
                        "start_line": match_lines[0] if len(match_lines) > 0 else 0,
                        "end_line": match_lines[1] if len(match_lines) > 1 else match_lines[0],
                        "column": match_position[0] if len(match_position) > 0 else 0,
                        "match_string": file_data.get("match_string", ""),
                        "metadata": {
                            "cwe": metadata.get("cwe", ""),
                            "owasp-web": metadata.get("owasp-web", ""),
                            "match_string": file_data.get("match_string", ""),
                        }
                    }

                    transformed_issues.append(transformed_issue)

        return transformed_issues

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        try:
            transformed_results = self.transform_output(raw_result)
            scan_result = super().parse_scan_result(transformed_results)

            nodejs_findings = len(raw_result.get("nodejs", {}))

            scan_result.scan_metadata.update({
                "nodejs_findings": nodejs_findings,
                "njsscan_version": raw_result.get("njsscan_version", "unknown")
            })

            return scan_result

        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing njsscan results: {str(e)}"
            )
