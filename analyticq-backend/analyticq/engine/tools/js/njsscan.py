from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import NjsScanAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import NjsScanParser
from analyticq.manager import AnalyticQContainerManager


class NjsScanTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "njsscan"
        image_tag = "latest"
        analyzer = NjsScanAnalyzer(container_manager, image_name, image_tag)
        parser = NjsScanParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
