from analyticq.engine.core.analyzer import AnalyticQAnalyzer
from analyticq.manager import AnalyticQContainerManager


class FlawFinderAnalyzer(AnalyticQAnalyzer):

    def __init__(self, container_manager: AnalyticQContainerManager, image_name: str, image_tag: str):
        self.container_manager = container_manager
        self.image_name = image_name
        self.image_tag = image_tag
        self.flawfinder_output_file = "flawfinder-report.csv"

    def get_output_filename(self):
        return "flawfinder-report.csv"
