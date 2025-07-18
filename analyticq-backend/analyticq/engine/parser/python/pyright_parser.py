from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class PyrightParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "rule",
            "message": "message",
            "path": "file",
            "start_line": "range.start.line",
            "end_line": "range.end.line",
            "start_column": "range.start.character",
            "end_column": "range.end.character",
            "severity": "severity",
            "message": "message",
        }
        super().__init__(tool_name="pyright", field_mapping=field_mapping)

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        if not isinstance(severity_level, str):
            return AnalyticQSeverity.UNKNOWN

        severity_mapping = {
            "none": AnalyticQSeverity.UNKNOWN,
            "error": AnalyticQSeverity.HIGH,
            "warning": AnalyticQSeverity.MEDIUM,
            "information": AnalyticQSeverity.INFO,
            "info": AnalyticQSeverity.INFO
        }

        return severity_mapping.get(severity_level.lower(), AnalyticQSeverity.UNKNOWN)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        try:
            if not isinstance(raw_result, dict):
                raise ScanParserException("Invalid Pyright result format: expected dictionary")
            # Normalize the raw_result into a list of issues
            pyright_issues = raw_result["generalDiagnostics"]
            if not isinstance(pyright_issues, list):
                raise ScanParserException("Invalid Pyright result format: generalDiagnostics must be a list")

            # Use the parent class to parse normalized issues
            scan = super().parse_scan_result(pyright_issues)

            raw_summary = raw_result.get("summary", {})
            if not isinstance(raw_summary, dict):
                raw_summary = {}

            scan.scan_metadata.update({
                "version": raw_result["version"],
                "metrics": {
                    "filesAnalyzed": raw_summary.get("filesAnalyzed", 0),
                    "errorCount": raw_summary.get("errorCount", 0),
                    "warningCount": raw_summary.get("warningCount", 0),
                    "informationCount": raw_summary.get("informationCount", 0)
                }
            })

            return scan

        except ScanParserException as e:
            raise e
        except (TypeError, AttributeError) as e:
            raise ScanParserException(f"Invalid Pyright result format: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing Pyright results: {str(e)}") from e
