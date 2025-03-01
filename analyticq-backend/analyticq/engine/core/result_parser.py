from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Union

from analyticq.exception import ScanParserException

from .models import (AnalyticQConfidence, AnalyticQSASTIssue,
                     AnalyticQSASTScanResult, AnalyticQSeverity)


class AnalyticQResultParser(ABC):

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
            "timestamp": datetime.now(UTC),
            "metrics": {},  # Default metrics (can be overridden)
        }

    @abstractmethod
    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        pass

    @abstractmethod
    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        pass

    def map_endline(self, end_line: Union[List, str]):
        if isinstance(end_line, list):
            return end_line[-1] if end_line else 0
        elif isinstance(end_line, str):
            return 0
        else:
            return end_line if end_line else 0

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResult:
        try:
            issues = []
            for raw_issue in raw_result:
                # Map fields using the tool-specific mapping
                severity = self._get_field(raw_issue, "severity", "unknown")
                confidence = self._get_field(raw_issue, "confidence", "unknown")
                issue = AnalyticQSASTIssue(
                    rule_id=self._get_field(raw_issue, "rule_id"),
                    severity=self._map_severity(severity),
                    confidence=self._map_confidence(confidence),
                    code=self._get_field(raw_issue, "code", default="Not present"),
                    message=self._get_field(raw_issue, "message", default="No message"),
                    path=self._get_field(raw_issue, "path", default="unknown"),
                    start_line=self._get_field(raw_issue, "start_line", default=0),
                    end_line=self.map_endline(self._get_field(raw_issue, "end_line", default=0)),
                    metadata=self._get_field(raw_issue, "metadata", default={})
                )
                issues.append(issue)

            summary = self._generate_summary(issues)
            metadata = self._generate_metadata()

            return AnalyticQSASTScanResult(
                scan_id="1",
                issues=issues,
                summary=summary,
                metadata=metadata
            )

        except (KeyError, TypeError) as e:
            raise ScanParserException(f"Failed to parse {self.tool_name} results: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing {self.tool_name} results: {str(e)}") from e
