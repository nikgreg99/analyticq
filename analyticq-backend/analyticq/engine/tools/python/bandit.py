from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import BanditAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import BanditParser
from analyticq.manager import AnalyticQContainerManager


class BanditTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "bandit"
        image_tag = "latest"
        analyzer = BanditAnalyzer(container_manager, image_name, image_tag)
        parser = BanditParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
