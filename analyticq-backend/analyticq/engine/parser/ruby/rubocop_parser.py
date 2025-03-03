from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class RubocopParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "rule_id",
            "message": "message",
            "path": "path",
            "start_line": "line",
            "endl_line": "line",
            "column": "column",
            "severity": "severity"
        }
        super().__init__(tool_name="rubocop", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        # According to https://docs.rubocop.org/rubocop/configuration.html#severity
        severity_map = {
            "refactor": AnalyticQSeverity.LOW,
            "convention": AnalyticQSeverity.LOW,
            "warning": AnalyticQSeverity.MEDIUM,
            "error": AnalyticQSeverity.HIGH,
            "fatal": AnalyticQSeverity.CRITICAL,
            "info": AnalyticQSeverity.INFO
        }
        return severity_map.get(severity_level, AnalyticQSeverity.UNKNOWN)

    def transform_output(self, raw_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        transformed_issues = []

        for file_data in raw_result.get("files", []):
            file_path = file_data.get("path", "unknown")
            for offense in file_data.get("offenses", []):
                location = offense.get("location", {})

                transformed_issue = {
                    "rule_id": offense.get("cop_name", "unknown"),
                    "path": file_path,
                    "message": offense.get("message", "unknown"),
                    "severity": offense.get("severity", "unknown"),
                    "line": location.get("line", "unknown"),
                    "column": location.get("column", "unknown"),
                }

                transformed_issues.append(transformed_issue)
        return transformed_issues

    def parse_scan_result(self, raw_result) -> AnalyticQSASTScanResult:
        try:
            transformed_results = self.transform_output(raw_result)
            scan_result = super().parse_scan_result(transformed_results)
            # Add Rubocop-specific metadata
            if "metadata" in raw_result:
                scan_result.metadata.update({
                    "rubocop_version": raw_result.get("metadata", {}).get("rubocop_version", "unknown"),
                    "ruby_engine": raw_result.get("metadata", {}).get("ruby_engine", "unknown"),
                    "ruby_version": raw_result.get("metadata", {}).get("ruby_version", "unknown"),
                    "ruby_patchlevel": raw_result.get("metadata", {}).get("ruby_patchlevel", "unknown"),
                    "ruby_platform": raw_result.get("metadata", {}).get("ruby_platform", "unknown")
                })

            if "summary" in raw_result:
                scan_result.metadata.update({
                    "offense_count": raw_result["summary"].get("offense_count", 0),
                    "target_file_count": raw_result["summary"].get("target_file_count", 0),
                    "inspected_file_count": raw_result["summary"].get("inspected_file_count", 0)
                })

            return scan_result
        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing Rubocop results: {str(e)}"
            ) from e
