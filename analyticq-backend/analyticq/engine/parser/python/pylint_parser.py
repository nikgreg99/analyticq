from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class PylintParser(AnalyticQResultParser):

    def __init__(self):

        field_mapping = {
            "code": "obj",
            "rule_id": "message-id",
            "start_line": "line",
            "message": "message",
            "path": "path",
            "end_line": "endLine",
            "severity": "type",
            "column": "column",
        }

        self.severity_mapping = {
            "info": "INFO",
            "convention": "LOW",
            "refactor": "LOW",
            "warning": "MEDIUM",
            "error": "HIGH",
            "fatal": "CRITICAL",
            "unknown": "UNKNOWN"
        }

        super().__init__(tool_name="Pylint", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        """
        Maps a pylint confidence level to an AnalyticQConfidence enum value.

        Args:
            confidence_level (str): The confidence level string from pylint

        Returns:
            AnalyticQConfidence: The corresponding AnalyticQConfidence enum value.
                Currently returns UNKNOWN for all inputs.
        """
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        mapped = self.severity_mapping.get(severity_level.lower(), "UNKNOWN")
        return AnalyticQSeverity.parse(mapped)

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        """
        Parses Pylint scan results into AnalyticQSASTScanResultModel format.
        This method processes raw Pylint scan results and converts them into the standardized
        AnalyticQSASTScanResultModel format used by AnalyticQ.
        Args:
            raw_result (Dict[str, Any]): Raw scan results from Pylint in dictionary format
        Returns:
            AnalyticQSASTScanResultModel: Parsed and formatted scan results
        Raises:
            ScanParserException: If raw_result is empty or if there is an error during parsing
        Example:
            parser = PylintParser()
            scan_result = parser.parse_scan_result(raw_pylint_output)
        """

        if not raw_result:
            raise ScanParserException("Empty raw result provided")

        try:
            return super().parse_scan_result(raw_result)
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing Pylint results: {str(e)}") from e
