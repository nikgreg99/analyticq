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
            "confidence": None,
            "column": "column",
            "issue_metadata": None
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

    def _preprocess_raw_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocesses the raw result from pylint analysis.
        Args:
            raw_result (Dict[str, Any]): Dictionary containing the raw pylint analysis results.
        Returns:
            Dict[str, Any]: A processed copy of the input dictionary with standardized format.
        """
        if isinstance(raw_result, dict):
            for result in raw_result:
                if result.get("messsage-id") is None:
                    result["message-id"] = "unkown"

        return raw_result

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        if not severity_level:
            return AnalyticQSeverity.UNKNOWN

        try:
            return AnalyticQSeverity.parse(self.severity_mapping[severity_level])
        except ValueError as e:
            raise ValueError(f"Invalid severity level: {severity_level}") from e

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

        processed_result = self._preprocess_raw_result(raw_result)

        try:
            return super().parse_scan_result(processed_result)
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing Pylint results: {str(e)}") from e
