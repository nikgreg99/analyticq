from analyticq.manager.jinja_manager import JinjaManager

from .report_generator import ReportGenerator


class HTMLReportGenerator(ReportGenerator):
    """A class for generating HTML reports from analysis results.
    This class extends the ReportGenerator base class and implements the generation
    of HTML reports using Jinja2 templates.
    Methods:
        generate() -> str: Generates an HTML report using the sast_report.html template
                          and returns it as a string.
    Returns:
        str: The rendered HTML report containing the analysis results.
    Example:
        generator = HTMLReportGenerator(results, timestamp)
        html_report = generator.generate()
    """
    def generate(self, path="sast_report.html") -> str :
        template = JinjaManager().get_template(path)

        data = self.get_base_data()
        data["formatted_timestamp"] = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        return template.render(**data)
