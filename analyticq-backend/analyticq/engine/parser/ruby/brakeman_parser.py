from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class BrakemanParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "warning_code",
            "code": "code",
            "severity": "severity",
            "confidence": "confidence",
            "message": "message",
            "path": "file",
            "start_line": "line",
            "end_line": "line",
            "issue_metadata": "metadata"
        }
        super().__init__(tool_name="brakeman", field_mapping=field_mapping)

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        """Maps Brakeman confidence levels to AnalyticQ severity levels.

        This method translates Brakeman's confidence levels into corresponding AnalyticQ severity levels.
        Brakeman uses confidence to indicate reliability of findings, which we map to severity levels.

        Args:
            severity_level (str): The confidence level from Brakeman ('High', 'Medium', or 'Low')

        Returns:
            AnalyticQSeverity: The corresponding AnalyticQ severity level (HIGH, MEDIUM, LOW, or UNKNOWN)

        Note:
            Brakeman confidence levels documentation:
            https://brakemanscanner.org/docs/options/#ConfidenceLevels
        """
        severity_map = {
            "High": AnalyticQSeverity.HIGH,
            "Medium": AnalyticQSeverity.MEDIUM,
            "Low": AnalyticQSeverity.LOW,
        }
        return severity_map.get(severity_level, AnalyticQSeverity.UNKNOWN)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        """
        Maps Brakeman confidence levels to AnalyticQ confidence levels.

        Args:
            confidence_level (str): The confidence level from Brakeman report
                                  (High, Medium, Low, or Weak)

        Returns:
            AnalyticQConfidence: The corresponding AnalyticQ confidence level enum value

        Note:
            - High -> AnalyticQConfidence.HIGH
            - Medium -> AnalyticQConfidence.MEDIUM
            - Low/Weak -> AnalyticQConfidence.LOW
            - Unknown values -> AnalyticQConfidence.UNKNOWN
        """
        confidence_map = {
            "High": AnalyticQConfidence.HIGH,
            "Medium": AnalyticQConfidence.MEDIUM,
            "Low": AnalyticQConfidence.LOW,
            "Weak": AnalyticQConfidence.LOW,
        }
        return confidence_map.get(confidence_level, AnalyticQConfidence.UNKNOWN)

    def transform_output(self, raw_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforms the raw Brakeman scan results into a standardized format.

        This method processes the raw JSON output from Brakeman security scanner and converts it into a list of
        standardized issue dictionaries. Each issue contains security warning details including warning codes,
        types, file locations, and associated metadata.

        Args:
            raw_result (Dict[str, Any]): The raw JSON output from Brakeman scan containing 'warnings' key
                with a list of security warnings.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries where each dictionary represents a transformed
            security issue with the following structure:
                {
                    'warning_code': str,
                    'warning_type': str,
                    'code': str,
                    'file': str,
                    'message': str,
                    'line': str,
                    'confidence': str,
                    'severity': str,
                    'metadata': {
                        'user_input': str,
                        'link': str,
                        'cwe_id': list
                    },
                    'location_type': str,  # Optional
                    'location_class': str, # Optional
                    'location_method': str # Optional
        """
        transformed_issues = []

        warnings = raw_result.get("warnings", [])

        for warning in warnings:
            loc = warning.get("location", {})

            transformed_issue = {
                "warning_code": str(warning.get("warning_code")),
                "warning_type": warning.get("warning_type", "Unknown"),
                "code": warning.get("code", ""),
                "file": warning.get("file", ""),
                "message": warning.get("message", ""),
                "line": warning.get("line", ""),
                "confidence": warning.get("confidence", ""),
                "severity": warning.get("severity", ""),
                "metadata": {
                    "user_input": warning.get("user_input", ""),
                    "link": warning.get("link", ""),
                    "cwe_id": warning.get("cwe_id", [])
                }
            }

            # Add location details if available
            if loc:
                transformed_issue["location_type"] = loc.get("type", "")
                transformed_issue["location_class"] = loc.get("class", "")
                transformed_issue["location_method"] = loc.get("method", "")

            transformed_issues.append(transformed_issue)

        return transformed_issues

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        try:
            scan_info = raw_result.get("scan_info", [])
            transformed_results = self.transform_output(raw_result)
            scan_result = super().parse_scan_result(transformed_results)

            if scan_info:
                scan_result.scan_metadata.update({
                    "brakeman_version": scan_info.get("brakeman_version", "unknown"),
                    "rails_version": scan_info.get("rails_version", "unknown"),
                    "ruby_version": scan_info.get("ruby_version", "unknown"),
                    "start_time": scan_info.get("start_time", "unknown"),
                    "end_time": scan_info.get("end_time", "unknown"),
                    "duration": scan_info.get("duration", 0),
                    "security_warnings": scan_info.get("security_warnings", 0),
                    "number_of_controllers": scan_info.get("number_of_controllers", 0),
                    "number_of_models": scan_info.get("number_of_models", 0),
                    "number_of_templates": scan_info.get("number_of_templates", 0)
                })

            # Add list of checks performed
            checks_performed = scan_info.get("checks_performed", [])
            if checks_performed:
                scan_result.scan_metadata["checks_performed"] = checks_performed

            scan_result.scan_metadata["metrics"] = {
                "total_warnings": len(raw_result.get("warnings", [])),
                "ignored_warnings": len(raw_result.get("ignored_warnings", []) or []),
                "errors": len(raw_result.get("errors", []) or [])
            }

            return scan_result

        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing Brakeman results: {str(e)}"
            ) from e
