from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import BearerAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import BearerParser
from analyticq.manager import AnalyticQContainerManager


class BearerTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "bearer"
        image_tag = "latest"
        container_manager.runtime_config.network.mode = "host"
        analyzer = BearerAnalyzer(container_manager, image_name, image_tag)
        parser = BearerParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
