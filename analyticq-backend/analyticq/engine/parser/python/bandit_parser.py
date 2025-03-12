from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class BanditParser(AnalyticQResultParser):
    def __init__(self):
        # Define field mapping from Bandit-specific fields to standard fields
        field_mapping = {
            "rule_id": "test_id",
            "severity": "issue_severity",
            "confidence": "issue_confidence",
            "message": "issue_text",
            "path": "filename",
            "start_line": "line_number",
            "end_line": "line_range",
            "code": "code",
            "issue_metadata": "issue_cwe"
        }
        super().__init__(tool_name="Bandit", field_mapping=field_mapping)

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        if not severity_level or not isinstance(severity_level, str):
            return AnalyticQSeverity.UNKNOWN

        try:
            return AnalyticQSeverity.parse(severity_level.upper())
        except ValueError as e:
            raise e

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        try:
            return AnalyticQConfidence.parse(confidence_level.upper())
        except ValueError as e:
            raise e

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        try:
            bandit_issues = raw_result.get("results", [])
            scan = super().parse_scan_result(bandit_issues)
            scan.scan_metadata.update({
                "metrics": raw_result.get("metrics", {}),
                "generated_at": raw_result.get("generated_at"),
            })
            return scan
        except ScanParserException as e:
            raise e
        except (TypeError, AttributeError) as e:
            raise ScanParserException(f"Invalid Bandit result format: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing Bandiit results: {str(e)}") from e
