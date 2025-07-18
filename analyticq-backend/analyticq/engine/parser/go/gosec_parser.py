import logging
from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException

logger = logging.getLogger(__name__)


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

    def _parse_line_number(self, line_value: Any) -> int:
        """
        Parse line number from Gosec output, handling both single numbers and ranges.

        Args:
            line_value: The line value from Gosec (could be int, str with number, or str with range)
        Returns:
            int: The starting line number
        Raises:
            ValueError: If the line value cannot be parsed
        """
        if isinstance(line_value, int):
            return line_value

        if isinstance(line_value, str):

            if '-' in line_value:
                try:
                    start_line = line_value.split('-')[0].strip()
                    return int(start_line)
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Cannot parse line range '{line_value}': {e}") from e
            else:
                # Handle single line number as string
                try:
                    return int(line_value.strip())
                except ValueError as e:
                    raise ValueError(f"Cannot parse line number '{line_value}': {e}") from e

        raise ValueError(f"Unsupported line value type: {type(line_value)} with value: {line_value}")

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

    def _transform_issue_data(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform issue data before creating the model, handling special cases like line ranges.

        Args:
            issue_data: Raw issue data from Gosec

        Returns:
            Dict[str, Any]: Transformed issue data ready for model creation
        """
        transformed_data = issue_data.copy()

        # Handle line number parsing for ranges
        if 'line' in transformed_data:
            try:
                transformed_data['line'] = self._parse_line_number(transformed_data['line'])
            except ValueError:
                # Log the error but don't fail the entire parsing - use a default value
                transformed_data['line'] = 1  # Default to line 1 if parsing fails
                # You might want to add logging here:
                logger.warning(f"Failed to parse line number: {transformed_data['line']}, defaulting to 1")

        return transformed_data

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        """
        Parse raw Gosec scan results into AnalyticQSASTScanResultModel
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
                raise ScanParserException("Invalid Gosec scan format: 'Issues' should be a list.")

            # Transform issues to handle line ranges and other special cases
            transformed_issues = []
            for issue in gosec_issues:
                transformed_issue = self._transform_issue_data(issue)
                transformed_issues.append(transformed_issue)

            scan = super().parse_scan_result(transformed_issues)
            scan.scan_metadata["GosecVersion"] = raw_result["GosecVersion"]
            scan.scan_metadata["metrics"] = raw_result["Stats"]
            return scan

        except ScanParserException as e:
            raise e
        except (TypeError, AttributeError) as e:
            raise ScanParserException(f"Invalid GoSec result format: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing GoSec results: {str(e)}") from e
