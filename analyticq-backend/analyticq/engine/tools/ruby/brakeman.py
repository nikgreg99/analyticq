from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import BrakemanAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import BrakemanParser
from analyticq.manager import AnalyticQContainerManager


class BrakemanTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "brakeman"
        image_tag = "latest"
        analyzer = BrakemanAnalyzer(container_manager, image_name, image_tag)
        parser = BrakemanParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
