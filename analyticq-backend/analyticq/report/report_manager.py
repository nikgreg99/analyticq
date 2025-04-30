from typing import Any

from analyticq.validator.scan import AnalyticQSASTScanResultModel

from .csv_report_generator import CSVReportGenerator
from .html_report_generator import HTMLReportGenerator
from .json_report_generator import JSONReportGenerator
from .pdf_report_generator import PDFReportGenerator
from .report_generator import ReportGenerator


class ReportManager:

    GENERATORS = {
        "json": JSONReportGenerator,
        "html": HTMLReportGenerator,
        "pdf": PDFReportGenerator,
        "csv": CSVReportGenerator
    }

    @staticmethod
    def get_generator(format_type: str, scan_result: AnalyticQSASTScanResultModel) -> ReportGenerator:
        """
        Creates and returns a specific report generator based on the requested format type.
        Args:
            format_type (str): The desired format type for the report (e.g., 'pdf', 'html').
            scan_result (AnalyticQSASTScanResultModel): The scan result data to be used for report generation.
        Returns:
            ReportGenerator: An instance of the appropriate report generator class.
        Raises:
            ValueError: If the specified format type is not supported.
        Example:
            >>> generator = get_generator('pdf', scan_result)
            >>> generator.generate()
        """
        generator_class = ReportManager.GENERATORS.get(format_type.lower())
        if not generator_class:
            raise ValueError(f"Unsupported format: {format_type}")

        return generator_class(scan_result)

    @staticmethod
    def generate_report(
        scan_result: AnalyticQSASTScanResultModel,
        format_type: str
    ) -> Any:
        """
        Generate a report from scan results in the specified format.

        Args:
            scan_result (AnalyticQSASTScanResultModel): Model containing the SAST scan results to be reported
            format_type (str): String specifying the desired output format of the report

        Returns:
            Any: Generated report in the specified format. Return type varies based on format_type.

        Raises:
            ValueError: If format_type is not supported
        """
        generator = ReportManager.get_generator(format_type, scan_result)
        return generator.generate()
