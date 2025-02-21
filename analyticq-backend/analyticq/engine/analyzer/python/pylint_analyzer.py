from analyticq.engine.core.analyzer import AnalyticQAnalyzer
from analyticq.manager import AnalyticQContainerManager


class PylintAnalyzer(AnalyticQAnalyzer):

    def __init__(self, container_manager: AnalyticQContainerManager, image_name: str, image_tag: str):
        self.container_manager = container_manager
        self.image_name = image_name
        self.image_tag = image_tag

    def get_output_filename(self):
        return "pylint-report.json"
