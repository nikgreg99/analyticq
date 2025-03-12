from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity


class StaticCheckParser(AnalyticQResultParser):

    def __init__(self):
        self.tool_name = "StaticCheck"
        field_mapping = {
            "rule_id": "code",
            "message": "message",
            "path": "location.file",
            "start_line": "location.line",
            "end_line": "end.line",
            "column": "location.column",
            "severity": "severity"
        }
        self.severity_mapping = {
            "error": "HIGH",       # StaticCheck's "error" maps to "HIGH"
            "warning": "MEDIUM",   # StaticCheck's "warning" maps to "MEDIUM"
            "info": "LOW",         # StaticCheck's "info" maps to "LOW"
            "unknown": "UNKNOWN"
        }
        super().__init__(tool_name="Staticcheck", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level: str) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level: str) -> AnalyticQSeverity:
        try:
            return AnalyticQSeverity.parse(self.severity_mapping[severity_level])
        except ValueError as e:
            raise ValueError(f"Invalid severity level: {severity_level}") from e
