from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class CheckStyleParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "ruleId",
            "message": "message.text",
            "path": "locations.0.physicalLocation.artifactLocation.uri",
            "start_line": "locations.0.physicalLocation.region.startLine",
            "end_line": "locations.0.pyshicalLocation.region.endLine",
            "column": "locations.0.physicalLocation.region.startColumn",
            "severity": "level",
            "code": "snippet",
            "issue_metadata": "metadata"
        }

        self.severity_map = {
            "error": AnalyticQSeverity.MEDIUM,  # Most Checkstyle errors are style issues
            "warning": AnalyticQSeverity.LOW,
            "info": AnalyticQSeverity.INFO,
        }

        super().__init__(tool_name="checkstyle", field_mapping=field_mapping)

    def _get_field(self, issue: Dict[str, Any], field: str, default: Any = None) -> Any:
        """
        Get a field value from issue dictionary using dot notation with array indexing.

        Args:
            issue: The issue dictionary
            field: The field name to retrieve (will be mapped using field_mapping)
            default: Default value if field not found

        Returns:
            The field value or default if not found
        """
        mapped_field = self.field_mapping.get(field)
        if not mapped_field:
            return default

        # Handle nested access using dot notation with array indexing
        value = issue
        try:
            for key in mapped_field.split("."):
                # Handle array indexing (e.g., "locations.0.physicalLocation")
                if key.isdigit():
                    key = int(key)
                value = value[key]
        except (KeyError, TypeError, IndexError):
            return default

        return value if value is not None else default

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        """Map SARIF severity levels to AnalyticQ severity."""
        return self.severity_map.get(severity_level.lower(), AnalyticQSeverity.UNKNOWN)

    def _map_confidence(sef, confidence_level: str) -> AnalyticQConfidence:
        """
        Map confidence levels to AnalyticQ confidence.
        Checkstyle typically doesn't include confidence, so we'll use HIGH for all.
        """
        return AnalyticQConfidence.UNKNOWN

    def _extract_rule_details(self, raw_result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract rule details from the SARIF file to provide additional context.


        Args:
            raw_result: Raw SARIF result dictionary

        Returns:
            Dictionary mapping rule IDs to their details
        """
        rule_details = {}
        try:
            rules = raw_result["runs"][0]["tool"]["driver"].get("rules", [])
            for rule in rules:
                rule_id = rule.get("id")
                if rule_id:
                    rule_details[rule_id] = {
                        "description": rule.get("shortDescription", {}).get("text", ""),
                        "help_uri": rule.get("helpUri", ""),
                        "tags": rule.get("properties", {}).get("tags", [])
                    }
        except (KeyError, IndexError):
            pass

        # If we didn't get any rules from the SARIF file, return an empty dict
        return rule_details

    def _categorize_checkstyle_rule(self, rule_id: str) -> str:
        """
        Categorize Checkstyle rules into common groups.
        Args:
            rule_id: The Checkstyle rule ID
        Returns:
            A category string for the rule
        """
        category_map = {
            "javadoc": "Documentation",
            "import": "Import Statements",
            "final": "Parameter Declaration",
            "maxLineLen": "Code Style",
            "magic": "Code Quality",
            "ws": "Whitespace",
            "needBraces": "Code Style",
            "name": "Naming Convention",
            "design": "Design",
            "maxParam": "Method Design",
            "block": "Code Structure"
        }

        for prefix, category in category_map.items():
            if rule_id.startswith(prefix):
                return category

        return "Other"

    def transform_sarif_to_issues(self, raw_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform SARIF format to a list of standardized issues.

        Args:
            raw_result: Raw SARIF result dictionary

        Returns:
            List of transformed issues in standard format

        Raises:
            ScanParserException: If parsing fails
        """
        transformed_issues = []
        try:
            # Extract rule details for additional context
            rule_details = self._extract_rule_details(raw_result)

            # Ensure we have at least one run
            if not raw_result.get("runs"):
                return transformed_issues

            # Process results from the first run
            results = raw_result["runs"][0].get("results", [])
            print("Getting results...")
            print(results)

            for result in results:
                transformed_issue = self._transform_single_issue(result, rule_details)
                transformed_issues.append(transformed_issue)

            return transformed_issues

        except KeyError as e:
            raise ScanParserException(
                f"Missing field while parsing Checkstyle SARIF results: {str(e)}"
            ) from e
        except Exception as e:
            raise ScanParserException(
                f"Unexpected error transforming Checkstyle SARIF results: {str(e)}"
            ) from e

    def _transform_single_issue(self, result: Dict[str, Any], rule_details: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Transform a single SARIF result into standardized issue format.

        Args:
            result: Single SARIF result dictionary
            rule_details: Dictionary of rule details by rule ID

        Returns:
            Transformed issue in standard format
        """
        rule_id = result.get("ruleId", "")
        rule_info = rule_details.get(rule_id, {})

        # Extract location info
        location = self._extract_location_info(result)

        # Get severity level
        level = result.get("level", "error")

        # Create metadata with rule categorization
        rule_category = self._categorize_checkstyle_rule(rule_id)

        metadata = {
            "rule_description": rule_info.get("description", ""),
            "help_uri": rule_info.get("help_uri", ""),
            "tags": rule_info.get("tags", []),
            "category": rule_category,
            "rule_id": rule_id
        }

        # Build the transformed issue
        return {
            "ruleId": rule_id,
            "message": {
                "text": result.get("message", {}).get("text", "")
            },
            "level": level,
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": location.get("uri", "")
                        },
                        "region": {
                            "startLine": location.get("startLine", 0),
                            "startColumn": location.get("startColumn", 0),
                            "endLine": location.get("endLine", location.get("startLine", 0)),
                            "endColumn": location.get("endColumn", 0)
                        }
                    }
                }
            ],
            "snippet": "",  # Checkstyle SARIF doesn't typically include code snippets
            "metadata": metadata
        }

    def _extract_location_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract location information from a SARIF result.

        Args:
            result: Single SARIF result dictionary

        Returns:
            Dictionary with uri, startLine, startColumn, endLine, and endColumn information
        """
        location = {
            "uri": "",
            "startLine": 0,
            "startColumn": 0,
            "endLine": 0,
            "endColumn": 0
        }

        if result.get("locations") and len(result["locations"]) > 0:
            physical_location = result["locations"][0].get("physicalLocation", {})
            region = physical_location.get("region", {})

            location = {
                "uri": physical_location.get("artifactLocation", {}).get("uri", ""),
                "startLine": region.get("startLine", 0),
                "startColumn": region.get("startColumn", 0),
                "endLine": region.get("endLine", region.get("startLine", 0)),
                "endColumn": region.get("endColumn", region.get("startColumn", 0))
            }

        return location

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        """
        Parse the Checkstyle SARIF results into the standardized AnalyticQSASTScanResult format.

        Args:
            raw_result: Raw SARIF result dictionary

        Returns:
            Standardized scan result

        Raises:
            ScanParserException: If parsing fails
        """
        try:
            transformed_results = self.transform_sarif_to_issues(raw_result)
            return super().parse_scan_result(transformed_results)
        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing Checkstyle SARIF results: {str(e)}"
            ) from e
