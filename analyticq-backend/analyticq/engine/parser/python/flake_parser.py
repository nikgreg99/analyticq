from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class FlakeParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "code",
            "severity": "code",  # Flake8 doesn't provide severity levels directly, use code instead
            "confidence": None,  # Flake8 doesn't provide confidence levels
            "message": "text",
            "path": "filename",
            "start_line": "line_number",
            "end_line": None,  # Flake8 doesn't provide end line
            "issue_metadata": None  # No additional metadata in standard Flake8 output
        }

        super().__init__(tool_name="flake8", field_mapping=field_mapping)

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        if not severity_level or not isinstance(severity_level, str):
            return AnalyticQSeverity.UNKNOWN

        prefix = severity_level[0].upper()

        return {
            'E': AnalyticQSeverity.HIGH,      # Error
            'F': AnalyticQSeverity.CRITICAL,  # Fatal
            'W': AnalyticQSeverity.MEDIUM,    # Warning
        }.get(prefix, AnalyticQSeverity.LOW)  # Default for C, N, etc.

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        """
        Maps a flake8 confidence level to an AnalyticQConfidence enum value.

        Args:
            confidence_level (str): The confidence level string from flake8.

        Returns:
            AnalyticQConfidence: The mapped confidence level, currently always returns UNKNOWN.
        """
        return AnalyticQConfidence.UNKNOWN

    def parse_scan_result(self, raw_result: Dict[str, List[Dict[str, Any]]]) -> AnalyticQSASTScanResultModel:
        """
        Parse raw Flake8 scan results into a standardized AnalyticQSASTScanResultModel.

        This method processes the raw dictionary output from Flake8 scans, normalizing the issues
        and adding Flake8-specific metadata like file counts and total issue counts.

        Args:
            raw_result (Dict[str, Any]): Raw scan results from Flake8 in dictionary format,
                where keys are filenames and values are lists of issues found in each file.

        Returns:
            AnalyticQSASTScanResultModel: A standardized scan result model containing the parsed
                and normalized Flake8 issues along with scan metadata.
        """
        try:
            # Normalize the raw_result into a list of issues
            flake8_issues = []

            for filename, issues in raw_result.items():
                for issue in issues:
                    # Add filename to issue if it doesn't already have it
                    if 'filename' not in issue:
                        issue['filename'] = filename
                    flake8_issues.append(issue)

            # Use the parent class to parse normalized issues
            scan = super().parse_scan_result(flake8_issues)

            # Add additional metadata specific to Flake8
            scan.scan_metadata.update({
                "metrics": {
                    "files_analyzed": len(raw_result.keys()),
                    "total_issues": len(flake8_issues)
                },
            })
            return scan

        except ScanParserException as e:
            raise e
        except (TypeError, AttributeError) as e:
            raise ScanParserException(f"Invalid Flake8 result format: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing Flake8 results: {str(e)}") from e
