from analyticq.engine.core import AnalyticQResultParser
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity


class PylintParser(AnalyticQResultParser):

    def __init__(self):

        field_mapping = {
            "code": "obj",
            "rule_id": "message-id",
            "start_line": "line",
            "message": "message",
            "path": "path",
            "end_line": "endLine",
            "severity": "type"
        }

        self.severity_mapping = {
            "convention": "LOW",
            "refactor": "LOW",
            "warning": "MEDIUM",
            "error": "HIGH",
            "fatal": "CRITICAL",
            "unknown": "UNKNOWN"
        }

        super().__init__(tool_name="Pylint", field_mapping=field_mapping)

    def _map_confidence(self, confidence_level) -> AnalyticQConfidence:
        return AnalyticQConfidence.UNKNOWN

    def _map_severity(self, severity_level) -> AnalyticQSeverity:
        try:
            return AnalyticQSeverity.parse(self.severity_mapping[severity_level])
        except ValueError as e:
            raise ValueError(f"Invalid severity level: {severity_level}") from e
