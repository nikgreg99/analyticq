from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class PHPStanParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "title",
            "message": "description",
            "path": "file_path",
            "start_line": "line_number",
            "end_line": "line_number",
            "issue_metadata": "metadata"
        }

        super().__init__(tool_name="PHPStan", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level) -> AnalyticQConfidence:
        return AnalyticQConfidence.LOW if confidence_level else AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        return AnalyticQSeverity.UNKNOWN

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        """
        Parse PHPSTan results using the base class parser.
        """
        try:
            files_data = raw_result.get("files", {})
            all_issues = []

            for file_path, file_data in files_data.items():
                messages = file_data.get("messages", [])
                for message in messages:
                    issue = {
                        "title": message["identifier"],
                        "description": message["message"],
                        "file_path": file_path,
                        "line_number": message["line"],
                        "metadata": {
                            "tip": message.get("tip", ""),
                            "identifier": message["identifier"]
                        }
                    }
                    all_issues.append(issue)

            scan_result = super().parse_scan_result(all_issues)
            scan_result.scan_metadata.update({
                "metrics": raw_result.get("totals", {}),
                "total_files_analyzed": len(files_data),
                "tool_specific": {
                    "errors": raw_result.get("errors", [])
                }
            })

            return scan_result

        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing PHPStan results: {str(e)}"
            ) from e
