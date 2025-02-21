from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import FlawFinderAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import FlawFinderParser
from analyticq.manager import AnalyticQContainerManager


class FlawFinderTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "flawfinder"
        image_tag = "latest"
        analyzer = FlawFinderAnalyzer(container_manager, image_name, image_tag)
        parser = FlawFinderParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
