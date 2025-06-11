from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class FlawFinderParser(AnalyticQResultParser):
    def __init__(self):
        field_mapping = {
            "rule_id": "RuleId",
            "message": "Warning",
            "path": "File",
            "start_line": "Line",
            "end_line": "Line",
            "severity": "Level",
            "code": "Context",
            "issue_metadata": "Metadata"
        }
        super().__init__(tool_name="FlawFinder", field_mapping=field_mapping)

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        """Map FlawFinder levels (1-5) to AnalyticQ severity levels."""
        severity_map = {
            "1": AnalyticQSeverity.LOW,
            "2": AnalyticQSeverity.LOW,
            "3": AnalyticQSeverity.MEDIUM,
            "4": AnalyticQSeverity.HIGH,
            "5": AnalyticQSeverity.CRITICAL
        }
        return severity_map.get(severity_level, AnalyticQSeverity.UNKNOWN)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        """FlawFinder doesn't provide confidence levels."""
        return AnalyticQConfidence.UNKNOWN

    def _parse_csv_to_dict(self, raw_result) -> List[Dict[str, Any]]:

        if not raw_result:
            return []

        transformed_issues = []
        for row in raw_result:
            # Enhance message with suggestion
            suggestion = row.get('Suggestion', '')
            warning = row.get('Warning', '')
            message = f"{warning} {suggestion}".strip()

            # Process CWEs
            cwes = [cwe.strip() for cwe in row.get('CWEs', '').split(',') if cwe.strip()] if row.get('CWEs') else []

            transformed_issue = {
                "RuleId": row.get('RuleId'),
                "Warning": message,
                "File": row.get('File'),
                "Line": row.get('Line', '0'),
                "Level": row.get('Level', '1'),
                "Context": row.get('Context', '').strip(),
                "Metadata": {
                    "category": row.get('Category'),
                    "cwes": cwes,
                    "help_uri": row.get('HelpUri'),
                }
            }
            transformed_issues.append(transformed_issue)

        return transformed_issues

    def parse_scan_result(self, raw_result: List[Dict[str, Any]]) -> AnalyticQSASTScanResultModel:
        """
        Parse FlawFinder CSV results using the base class parser.
        """
        try:
            # Transform CSV into dictionary format
            transformed_results = self._parse_csv_to_dict(raw_result)

            # Use base class's parse_scan_result
            return super().parse_scan_result(transformed_results)

        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing FlawFinder results: {str(e)}"
            ) from e
