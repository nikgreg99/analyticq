import json
from typing import Any, Dict

from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException


class BanditResultParser(AnalyticQResultParser):

    def __init__(self):
        self.tool_name = "Bandit"

    def parse_scan_result(self, raw_results: Dict[str, Any]) -> AnalyticQSASTScanResult:
        try:
            issues = [
                AnalyticQSASTIssue(
                    issue_id="1",
                    rule_id=issue["test_id"],
                    severity=AnalyticQSeverity.parse(issue["issue_severity"].upper()),
                    confidence=AnalyticQConfidence.parse(issue["issue_confidence"].upper()),
                    code=issue["code"],
                    message=issue["issue_text"],
                    path=issue["filename"],
                    start_line=issue["line_number"],
                    end_line=issue["line_range"][-1]
                )
                for issue in raw_results.get("results", [])
            ]

            summary = {
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

            metadata = {
                "tool": self.tool_name,
                "metrics": raw_results.get("metrics", {})
            }

            return AnalyticQSASTScanResult(
                scan_id="1",
                issues=issues,
                summary=summary,
                metadata=metadata
            )
        except (KeyError, json.decoder.JSONDecodeError) as e:
            raise ScanParserException(
                f"Failed to parse Bandit results: {str(e)}"
            ) from e
        except Exception as e:
            raise ScanParserException(
                f"Unexpected error parsing results: {str(e)}"
            ) from e
