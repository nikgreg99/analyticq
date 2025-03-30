import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Union

from analyticq.exception import ScanParserException

from .models import (AnalyticQConfidence, AnalyticQSASTIssueModel,
                     AnalyticQSASTScanResultModel, AnalyticQSeverity)


class AnalyticQResultParser(ABC):
    """Abstract base class for parsing security analysis tool results into a standardized format.

    This class provides a framework for converting tool-specific output formats into a
    standardized AnalyticQ format. It handles field mapping, severity levels, confidence
    levels, and metadata processing.

    Attributes:
        tool_name (str): Name of the security analysis tool being used
        field_mapping (Dict[str, str]): Mapping between tool-specific and standardized field names

        ```python
        class CustomToolParser(AnalyticQResultParser):
            def __init__(self):
                    "severity": "impact.severity",
                    "confidence": "reliability",
                    "rule_id": "check.id"
                super().__init__("CustomTool", field_mapping)
        ```

    Notes:
        - Subclasses must implement _map_severity and _map_confidence methods
        - The field_mapping dictionary supports dot notation for nested fields
        - All parsing methods include error handling for malformed input

        ScanParserException: When parsing fails due to invalid input format or unexpected errors

    See Also:
        AnalyticQSASTScanResultModel: The output model for parsed results
        AnalyticQSeverity: Enumeration of standardized severity levels
        AnalyticQConfidence: Enumeration of standardized confidence levels
    """
    def __init__(self, tool_name: str, field_mapping: Dict[str, str]):
        """
        Args:
            tool_name (str): The name of the tool being used for parsing.
            field_mapping (Dict[str, str]): A dictionary mapping the field names from the tool's output
                to standardized field names used in the application.

        Example:
            field_mapping = {
                "tool_specific_field": "standard_field",
                "severity": "risk_level"
            }
        """
        self.tool_name = tool_name
        self.field_mapping = field_mapping

    def _get_field(self, issue: Dict[str, Any], field: str, default: Optional[Any] = None) -> Any:
        """
        Gets the value of a field from an issue dictionary using field mapping.

        Args:
            issue (Dict[str, Any]): The issue dictionary containing field data
            field (str): The field name to retrieve
            default (Optional[Any], optional): Default value if field not found. Defaults to None.

        Returns:
            Any: The value of the mapped field from the issue, or the default value if not found

        Example:
            >>> parser = ResultParser()
            >>> issue = {"summary": "Bug report"}
            >>> parser._get_field(issue, "title", "No title")
            'Bug report'  # Assuming "title" is mapped to "summary" in field_mapping
        """
        mapped_field = self.field_mapping.get(field)
        if not mapped_field:
            return default

        # Handle nested access using dot notation
        value = issue
        try:
            for key in mapped_field.split("."):
                value = value[key]
        except (KeyError, TypeError):
            return default

        return value if value is not None else default

    def _generate_summary(self, issues: List) -> Dict[str, Any]:
        return {
            "total": len(issues),
            "by_severity": {
                severity.value: sum(1 for issue in issues if issue.severity == severity)
                for severity in AnalyticQSeverity
            },
            "by_confidence": {
                confidence.value: sum(1 for issue in issues if issue.confidence == confidence)
                for confidence in AnalyticQConfidence
            }
        }

    def _generate_metadata(self) -> Dict[str, Any]:
        """
        Generate metadata for the analysis result.
        This method creates a dictionary containing basic metadata about the analysis run,
        including the tool name and empty metrics dictionary that can be populated later.
        """
        return {
            "tool_name": f"{self.tool_name}",
            "timestamp": datetime.now(UTC).strftime("%d/%m/%Y, %H:%M:%S"),
            "metrics": {},  # Default metrics (can be overridden)
        }

    @abstractmethod
    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        """
        Maps a severity level string to an AnalyticQSeverity enum value.

        Args:
            severity_level (str): The severity level string to be mapped.

        Returns:
            AnalyticQSeverity: The corresponding AnalyticQSeverity enum value.

        Raises:
            ValueError: If the provided severity_level string cannot be mapped to a valid AnalyticQSeverity.
        """
        pass

    @abstractmethod
    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        """Maps a confidence level string to an AnalyticQConfidence enum.

        This method translates string-based confidence levels into their corresponding
        AnalyticQConfidence enum values used internally by the system.

        Args:
            confidence_level (str): The string representation of the confidence level

        Returns:
            AnalyticQConfidence: The corresponding confidence enum value

        Raises:
            ValueError: If the confidence_level string cannot be mapped to a valid enum value
        """
        pass

    def map_endline(self, end_line: Union[List, str]):
        """
        Maps the end line of a code block based on different input types.

        Args:
            end_line (Union[List, str]): The end line identifier that can be either a list, string, or numeric value.

        Returns:
            int: The mapped end line number:
                - For lists: returns the last element if list is not empty, otherwise 0
                - For strings: returns 0
                - For other types: returns the input value if not None/empty, otherwise 0
        """
        if isinstance(end_line, list):
            return end_line[-1] if end_line else 0
        elif isinstance(end_line, str):
            return 0
        else:
            return end_line if end_line else 0

    def _process_metadata(self, raw_issue: Dict[str, Any]) -> Dict[str, Any]:

        metadata_field = self.field_mapping.get("issue_metadata")
        if not metadata_field:
            return {}
        try:
            metadata = raw_issue
            for key in metadata_field.split("."):
                if key in metadata:
                    metadata = metadata[key]
                else:
                    return {}

                if isinstance(metadata, dict):
                    # Copy all fields from the original metadata dictionary
                    processed_metadata = {k: v for k, v in metadata.items()}
                    return processed_metadata
                elif isinstance(metadata, list):
                    processed_metadata = {}
                    processed_metadata = {"items": metadata}
                else:
                    # For simple values, wrap them in a dictionary
                    return {"value": metadata}
        except (KeyError, TypeError):
            return {}  # Return empty dict on any error

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        try:
            issues = []
            for raw_issue in raw_result:
                # Map fields using the tool-specific mapping
                severity = self._get_field(raw_issue, "severity", "unknown")
                confidence = self._get_field(raw_issue, "confidence", "unknown")

                procossed_metadata = self._process_metadata(raw_issue)

                issue = AnalyticQSASTIssueModel(
                    rule_id=self._get_field(raw_issue, "rule_id"),
                    severity=self._map_severity(severity),
                    confidence=self._map_confidence(confidence),
                    code=self._get_field(raw_issue, "code", default="Not present"),
                    message=self._get_field(raw_issue, "message", default="No message"),
                    path=self._get_field(raw_issue, "path", default="unknown"),
                    start_line=self._get_field(raw_issue, "start_line", default=0),
                    end_line=self.map_endline(self._get_field(raw_issue, "end_line", default=0)),
                    issue_metadata=procossed_metadata
                )
                issues.append(issue)

            summary = self._generate_summary(issues)
            metadata = self._generate_metadata()
            new_scan_id = str(uuid.uuid4())

            return AnalyticQSASTScanResultModel(
                scan_id=str(new_scan_id),
                issues=issues,
                summary=summary,
                tool_name=self.tool_name,
                scan_metadata=metadata
            )

        except (KeyError, TypeError) as e:
            raise ScanParserException(f"Failed to parse {self.tool_name} results: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing {self.tool_name} results: {str(e)}") from e
