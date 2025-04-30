from .report_generator import ReportGenerator


class CSVReportGenerator(ReportGenerator):
    """Generate CSV report."""

    def generate(self) -> str:
        """Generate a CSV report from scan results.
        This method creates a CSV report containing security scan results. The report includes
        details about each issue found during the scan, such as rule IDs, severity levels,
        confidence ratings, file paths, line numbers, and issue messages.
        Returns:
            str: A string containing the CSV data with the following columns:
                - Rule ID: The identifier of the security rule that was triggered
                - Severity: The severity level of the issue
                - Confidence: The confidence level of the finding
                - Path: The file path where the issue was found
                - Lines: The range of lines where the issue occurs (format: "start_line-end_line")
                - Message: The description of the security issue
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "Rule ID", "Severity", "Confidence", "Path", "Lines", "Message"
        ])

        # Write issues
        for issue in self.scan_result.issues:
            severity = getattr(issue.severity, "value", str(issue.severity))
            confidence = getattr(issue.confidence, "value", str(issue.confidence))

            writer.writerow([
                issue.rule_id,
                severity,
                confidence,
                issue.path,
                f"{issue.start_line}-{issue.end_line}",
                issue.message
            ])

        return output.getvalue()
