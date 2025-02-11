from abc import ABC, abstractmethod
from typing import Any, Dict

from .models import AnalyticQSASTScanResult


class AnalyticQResultParser(ABC):
    SCHEMA_VERSION = "1.0.0"

    @abstractmethod
    def parse_scan_result(self, raw_result: Dict[str, Any]) -> AnalyticQSASTScanResult:
        """Parse the raw scan results into a structured AnalyticQSASTScanResult object.

        This method converts raw scanning results from various SAST tools into a standardized
        AnalyticQSASTScanResult format for consistent processing across the application.

        Args:
            raw_result (Dict[str, Any]): Raw scan results dictionary containing findings from SAST tools.

        Returns:
            AnalyticQSASTScanResult: Structured object containing parsed scan results with standardized fields.

        Raises:
            ParsingError: If the raw result format is invalid or cannot be parsed.
        """
        pass
