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
        if not confidence_level or not isinstance(confidence_level, str):
            return AnalyticQSeverity.UNKNOWN

        try:
            return AnalyticQConfidence.parse(confidence_level.upper())
        except ValueError as e:
            raise ScanParserException(f"Invalid severity level '{confidence_level}': {str(e)}") from e

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        """
        Parse the raw results from a Bandit SAST scan into a standardized format.

        This method processes the raw JSON output from a Bandit security scan, extracts relevant
        information about identified issues, and converts it into an AnalyticQSASTScanResultModel object.

        Args:
            raw_result (Dict[str, Any]): The raw scan results from Bandit in dictionary format.
                Expected to contain 'results', 'metrics', and 'generated_at' keys.

        Returns:
            AnalyticQSASTScanResultModel: A standardized scan result object containing the parsed
                security issues and metadata from the Bandit scan.

        Raises:
            ScanParserException: If there are any errors parsing the scan results, including:
                - Invalid result format
                - Missing required fields
                - Unexpected data structures
            TypeError: If the input data types are incorrect
            AttributeError: If required attributes are missing from the input
        """
        if not isinstance(raw_result, dict):
            raise ScanParserException("Raw result must be a dictionary")

        try:
            bandit_issues = raw_result.get("results", [])

            if not isinstance(bandit_issues, list):
                raise ScanParserException("'results' field must be a list")

            scan = super().parse_scan_result(bandit_issues)

            metrics = raw_result.get("metrics", {})
            if not isinstance(metrics, dict):
                metrics = {}

            generated_at = raw_result.get("generated_at")

            scan.scan_metadata.update({
                "metrics": metrics,
                "generated_at": generated_at
            })
            return scan
        except ScanParserException as e:
            raise e
        except (TypeError, AttributeError) as e:
            raise ScanParserException(f"Invalid Bandit result format: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing Bandiit results: {str(e)}") from e
