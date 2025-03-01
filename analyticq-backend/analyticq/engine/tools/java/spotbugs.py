from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import SpotBugsAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import SpotBugsParser
from analyticq.manager import AnalyticQContainerManager


class SpotBugTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "spotbugs"
        image_tag = "latest"
        analyzer = SpotBugsAnalyzer(container_manager, image_name, image_tag)
        parser = SpotBugsParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
