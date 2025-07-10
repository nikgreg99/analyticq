from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class GoSecParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "rule_id",
            "severity": "severity",
            "confidence": "confidence",
            "path": "file",
            "message": "details",
            "start_line": "line",
            "column": "column",
            "code": "code",
            "issue_metadata": "cwe"
        }

        super().__init__(tool_name="gosec", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        """
        Maps the confidence level from the gosec report to AnalyticQConfidence enum.

        Args:
            confidence_level (str): The confidence level from gosec report

        Returns:
            AnalyticQConfidence: The mapped confidence level as AnalyticQConfidence enum value

        Raises:
            ValueError: If the confidence level cannot be parsed into a valid AnalyticQConfidence
        """
        try:
            return AnalyticQConfidence.parse(confidence_level)
        except ValueError as e:
            raise ValueError(f"Invalid confidence level: {confidence_level}") from e

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        try:
            return AnalyticQSeverity.parse(severity_level)
        except ValueError as e:
            raise ValueError(f"Invalid severity level: {severity_level}") from e

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        """
        Parse raw Gosec scan results into AnalyticQSASTScanResultModel.

        Args:
            raw_result (Dict[str, Any]): Raw scan results from Gosec scanner containing issues,
                version and metrics information.

        Returns:
            AnalyticQSASTScanResultModel: Parsed scan results in standardized format.

        Raises:
            ScanParserException: If there are issues parsing the scan results due to:
                - Invalid result format
                - Missing required fields
                - Unexpected errors during parsing
        """
        try:
            gosec_issues = raw_result["Issues"]
            if not isinstance(gosec_issues, list):
                raise ScanParserException("Invalid Gosec scan format: 'Issues  should be a list.")
            scan = super().parse_scan_result(gosec_issues)
            scan.scan_metadata["GosecVersion"] = raw_result["GosecVersion"]
            scan.scan_metadata["metrics"] = raw_result["Stats"]
            return scan
        except ScanParserException as e:
            raise e
        except (TypeError, AttributeError) as e:
            raise ScanParserException(f"Invalid GoSec result format: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing GoSec results: {str(e)}") from e
