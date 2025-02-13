from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class PylintParser(AnalyticQResultParser):

    def __init__(self):
        self.tool_name = "Pylint"

    def parse_scan_result(self, raw_result: Dict[str, Any]):
        try:
            issues = []
            # Map Pylint issue types to SAST severity levels
            for result in raw_result:
                severity_map = {
                    "convention": "LOW",
                    "refactor": "LOW",
                    "warning": "MEDIUM",
                    "error": "HIGH",
                    "fatal": "CRITICAL",
                }
                severity = severity_map.get(result["type"], "LOW")

                # Create SASTFinding object
                issue = AnalyticQSASTIssue(
                    issue_id="1",
                    code=result["obj"],
                    rule_id=result["message-id"],
                    severity=AnalyticQSeverity.parse(severity),
                    message=result["message"],
                    path=result["path"],
                    start_line=result["line"],
                    end_line=result.get("endLine") if result.get("endLine") is not None else 0,  # Use line if endLine is missing
                    confidence=AnalyticQConfidence.UNKNOWN,  # Pylint doesn't provide confidence, default to HIGH
                )

                issues.append(issue)

            summary = {
                "total": len(issues),
                "by_severity": {
                    severity.value: sum(1 for issue in issues if issue.severity == severity)
                    for severity in AnalyticQSeverity
                }
            }

            # Generate metadata
            metadata = {
                "tool": self.tool_name,
                "metrics": {},  # Pylint doesn't provide metrics by default
            }

            return AnalyticQSASTScanResult(
                scan_id="2",
                issues=issues,
                summary=summary,
                metadata=metadata
            )

        except (KeyError, TypeError) as e:
            raise ScanParserException(f"Failed to parse Pylint results: {str(e)}") from e
        except Exception as e:
            raise ScanParserException(f"Unexpected error parsing results: {str(e)}") from e
