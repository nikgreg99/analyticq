from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class StaticCheckParser(AnalyticQResultParser):

    def __init__(self):
        self.tool_name = "StaticCheck"

    def parse_scan_result(self, raw_result: Dict[str, Any]):
        try:
            issues = []
            severity_map = {
                "error": "HIGH",       # StaticCheck's "error" maps to "HIGH"
                "warning": "MEDIUM",   # StaticCheck's "warning" maps to "MEDIUM"
                "info": "LOW",         # StaticCheck's "info" maps to "LOW"
            }

            for result in raw_result:
                severity = severity_map.get(result["severity"], "LOW")

                issue = AnalyticQSASTIssue(
                    issue_id=result.get("code", "1"),  # Use the "code" field as the issue ID
                    code=result.get("code", ""),
                    rule_id=result.get("code", ""),
                    severity=AnalyticQSeverity.parse(severity),
                    message=result.get("message", ""),
                    path=result["location"]["file"],
                    start_line=result["location"]["line"],
                    end_line=result["end"]["line"],
                    confidence=AnalyticQConfidence.UNKNOWN,  # StaticCheck doesn't provide confidence, default to UNKNOWN
                )

                issues.append(issue)

            summary = {
                "total": len(issues),
                "by_severity": {
                    severity.value: sum(1 for issue in issues if issue.severity == severity)
                    for severity in AnalyticQSeverity
                }
            }

            metadata = {
                "tool": self.tool_name,
                "metrics": {}  # StaticCheck doesn't provivde metrics by default
            }

            return AnalyticQSASTScanResult(
                scan_id="2",  # Replace with actual scan ID if available
                issues=issues,
                summary=summary,
                metadata=metadata
            )

        except (KeyError, TypeError) as e:
            raise ScanParserException(f"Failed to parse StaticCheck results: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing results: {str(e)}") from e
