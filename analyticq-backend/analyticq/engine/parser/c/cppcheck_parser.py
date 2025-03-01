from typing import Any, Dict, List

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTScanResult,
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
            "severity": "severity",
            "code": "verbose",
            "metadata": "metadata"
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

    def _map_confidence(self, confidence_level) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level) -> AnalyticQSeverity:
        return self.severity_map.get(severity_level.lower(), AnalyticQSeverity.UNKNOWN)

    def parse_locations(self, issue_data: Dict) -> List[Dict[str, Any]]:
        locations = []
        if 'location' in issue_data.get('children', {}):
            loc_data = issue_data['children']['location']
        if isinstance(loc_data, list):
            for loc in loc_data:
                locations.append({
                    "file": loc["attributes"].get("file", ""),
                    "line": loc["attributes"].get("line", "0"),
                    "column": loc["attributes"].get("column", "0"),
                    'info': loc['attributes'].get('info', '')
                })
        else:
            locations.append({
                'file': loc_data['attributes'].get('file', ''),
                'line': loc_data['attributes'].get('line', '0'),
                'column': loc_data['attributes'].get('column', '0'),
                'info': loc_data['attributes'].get('info', '')
            })

        return locations

    def parse_xml_to_dict(self, raw_result: Dict) -> List[Dict[str, Any]]:
        transormed_issues = []
        try:
            issues = raw_result['children']['errors']['children']['error']
            if not isinstance(issues, list):
                issues = issues

            for issue in issues:
                attributes = issue['attributes']
                locations = self.parse_locations(issue)

                primary_loc = locations[0] if locations else {
                    "file": "",
                    "line": "0",
                    "column:": "0",
                }

                transormed_issue = {
                    "id": attributes.get('id', ''),
                    "msg": attributes.get('msg', ''),
                    "file": primary_loc['file'],
                    "line": primary_loc['line'],
                    "severity": attributes.get('severity', 'low'),
                    "metadata": {
                        "cwe": attributes.get('cwe', ''),
                        "all_locations": locations,
                        "symbol": issue.get('children', {}).get('symbol', {}).get('text', ''),
                        "help_uri": f"https://cppcheck.sourceforge.io/docs/data-{attributes.get('id', '')}.html"
                    }
                }
                transormed_issues.append(transormed_issue)

                return transormed_issues

        except KeyError as e:
            raise ScanParserException(
                f"Missing field while in CppCheck results: {str(e)}"
            ) from e

    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResult:
        try:
            transformed_results = self.parse_xml_to_dict(raw_result)
            return super().parse_scan_result(transformed_results)
        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing CppCheck results: {str(e)}"
            ) from e
