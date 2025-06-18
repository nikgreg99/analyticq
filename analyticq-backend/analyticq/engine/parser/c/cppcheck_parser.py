from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class CppCheckParser(AnalyticQResultParser):

    def __init__(self):
        field_mapping = {
            "rule_id": "id",
            "message": "msg",
            "path": "file",
            "start_line": "line",
            "end_line": "line",
            "column": "column",
            "severity": "severity",
            "code": "verbose",
            "issue_metadata": "metadata"
        }
        self.severity_map = {
            "error": AnalyticQSeverity.HIGH,
            "warning": AnalyticQSeverity.MEDIUM,
            "style": AnalyticQSeverity.LOW,
            "performance": AnalyticQSeverity.MEDIUM,
            "information": AnalyticQSeverity.INFO,
            "portability": AnalyticQSeverity.LOW
        }
        super().__init__(tool_name="cppcheck", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        """
        Maps confidence levels from Cppcheck to AnalyticQ confidence levels.

        Args:
            confidence_level (str): The confidence level string from Cppcheck

        Returns:
            AnalyticQConfidence: The mapped AnalyticQ confidence level, currently always returns UNKNOWN
        """
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        """
        Maps the severity level from the cppcheck format to the AnalyticQ severity level.

        Args:
            severity_level (str): The severity level string from cppcheck output.

        Returns:
            AnalyticQSeverity: The corresponding AnalyticQ severity level. Returns UNKNOWN if mapping not found.
        """
        return self.severity_map.get(severity_level.lower(), AnalyticQSeverity.UNKNOWN)

    def parse_locations(self, issue_data: Dict) -> List[Dict[str, Any]]:
        locations = []
        if 'location' not in issue_data.get('children', {}):
            return locations

        loc_data = issue_data['children']['location']

        if isinstance(loc_data, list):
            location_list = loc_data
        else:
            location_list = [loc_data]

        for loc in location_list:
            attributes = loc.get('attributes', {})
            location_info = {
                "file": attributes.get("file", ""),  # filename (relative or absolute path)
                "file0": attributes.get("file0", ""),  # source file name (optional)
                "line": int(attributes.get("line", "0")),
                "column": int(attributes.get("column", "0")) if attributes.get("column") else None,
                "info": attributes.get("info", "")  # short information for each location (optional)
            }

            if not location_info["file0"]:
                del location_info["file0"]
            if location_info["column"] is None:
                del location_info["column"]

            locations.append(location_info)

        return locations

    def parse_xml_to_dict(self, raw_result: Dict) -> List[Dict[str, Any]]:
        transformed_issues = []
        try:
            issues = raw_result['children']['errors']['children']['error']
            if not isinstance(issues, list):
                issues = [issues]

            for issue in issues:
                attributes = issue['attributes']
                locations = self.parse_locations(issue)

                primary_loc = locations[0] if locations else {
                    "file": "",
                    "line": "0",
                    "column:": "0"
                }

                transformed_issue = {
                    "id": attributes.get('id', ''),
                    "msg": attributes.get('msg', ''),
                    "file": primary_loc['file'],
                    "line": primary_loc['line'],
                    "severity": attributes.get('severity', 'low'),
                    "metadata": {
                        "cwe": attributes.get('cwe', ''),
                        "verbose": attributes.get('verbose', ''),
                        "symbol": issue.get('children', {}).get('symbol', {}).get('text', ''),
                        "help_uri": f"https://cppcheck.sourceforge.io/docs/data-{attributes.get('id', '')}.html",
                        "locations": {
                            "primary": locations[0] if locations else None,
                            "count": len(locations)
                        }
                    }
                }

                transformed_issues.append(transformed_issue)

            return transformed_issues

        except KeyError as e:
            raise ScanParserException(
                f"Missing field while in CppCheck results: {str(e)}"
            ) from e

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResultModel:
        """
        Parse the scan results from CppCheck XML output into AnalyticQSASTScanResultModel.

        This method transforms the raw XML results from CppCheck into a standardized
        scan result model by first converting the XML to a dictionary and then
        passing it to the parent class parser.

        Args:
            raw_result (Dict[str, Any]): Raw scan results from CppCheck in XML format

        Returns:
            AnalyticQSASTScanResultModel: Parsed and standardized scan results

        Raises:
            ScanParserException: If there is an error parsing the CppCheck results
        """
        try:
            transformed_results = self.parse_xml_to_dict(raw_result)
            return super().parse_scan_result(transformed_results)
        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing CppCheck results: {str(e)}"
            ) from e
