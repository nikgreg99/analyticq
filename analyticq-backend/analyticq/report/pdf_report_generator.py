import logging
import os
import tempfile
import uuid
from pathlib import Path

import xhtml2pdf.pisa as pisa

from .html_report_generator import HTMLReportGenerator
from .report_generator import ReportGenerator

TEMP_DIR = Path(tempfile.gettempdir()) / "analyticq_reports"
os.makedirs(TEMP_DIR, exist_ok=True)

logger = logging.getLogger(__name__)


class PDFReportGenerator(ReportGenerator):

    def generate(self) -> bytes:
        """
        Generates a PDF report from scan results by first creating an HTML report and then converting it to PDF.
        The function follows these steps:
        Returns:
            bytes: The generated PDF report content as bytes
        Raises:
            Exception: If there is an error during PDF generation or file operations
        Notes:
            - Uses pdfkit for HTML to PDF conversion
            - Temporary files are created with UUID to avoid conflicts
            - Temporary files are cleaned up even if an error occurs
            - PDF is generated with A4 page size and 0.75 inch margins
        """

        html_generator = HTMLReportGenerator(self.scan_result)
        html_content = html_generator.generate(path="sast_report_pdf.html")

        temp_id = uuid.uuid4().hex
        temp_html_path = TEMP_DIR / f"temp_{temp_id}.html"
        temp_pdf_path = TEMP_DIR / f"temp_{temp_id}.pdf"

        try:
            with open(temp_pdf_path, "wb") as pdf_file:
                pisa.CreatePDF(
                    html_content,
                    dest=pdf_file,
                )

            with open(temp_pdf_path, 'rb') as f:
                pdf_bytes = f.read()

            return pdf_bytes

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
        finally:
            for path in [temp_html_path, temp_pdf_path]:
                if path.exists():
                    try:
                        path.unlink()
                    except Exception as e:
                        logger.error(f"Error cleaning up temp file {path}: {str(e)}")
