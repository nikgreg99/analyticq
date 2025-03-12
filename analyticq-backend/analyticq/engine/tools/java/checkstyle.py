from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import CheckStyleAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import CheckStyleParser
from analyticq.manager import AnalyticQContainerManager


class CheckStyleTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "checkstyle"
        image_tag = "latest"
        container_manager.runtime_config.network.mode = "host"  # Need to download default XML cofig for making analysis
        analyzer = CheckStyleAnalyzer(container_manager, image_name, image_tag)
        parser = CheckStyleParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
