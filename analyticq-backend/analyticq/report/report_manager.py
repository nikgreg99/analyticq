from typing import Any, Dict, Type

from analyticq.validator.scan import AnalyticQSASTScanResultModel

from .csv_report_generator import CSVReportGenerator
from .html_report_generator import HTMLReportGenerator
from .json_report_generator import JSONReportGenerator
from .pdf_report_generator import PDFReportGenerator
from .report_generator import ReportGenerator


class ReportManager:

    GENERATORS: Dict[str, Type[ReportGenerator]] = {
        "json": JSONReportGenerator,
        "html": HTMLReportGenerator,
        "pdf": PDFReportGenerator,
        "csv": CSVReportGenerator
    }

    @classmethod
    def register_format(cls, format_type: str, generator_class: Type[ReportGenerator]) -> None:
        """
        Register a new report format and its corresponding generator class.

        This class method adds a new report format type and its associated generator class to the
        GENERATORS dictionary. The format type is stored in lowercase to ensure case-insensitive matching.

        Args:
            format_type (str): The identifier for the report format (e.g., 'pdf', 'csv', etc.)
            generator_class (Type[ReportGenerator]): The class responsible for generating reports in the specified format.
                                                   Must be a subclass of ReportGenerator.

        Returns:
            None

        Example:
            >>> ReportManager.register_format('pdf', PDFGenerator)
        """
        cls.GENERATORS[format_type.lower()] = generator_class

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
        """
        generator_class = ReportManager.GENERATORS.get(format_type.lower())
        if not generator_class:
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats are: {', '.join(ReportManager.GENERATORS.keys())}"
            )

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
