from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import RubocopAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import RubocopParser
from analyticq.manager import AnalyticQContainerManager


class RubocopTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "rubocop"
        image_tag = "latest"
        analyzer = RubocopAnalyzer(container_manager, image_name, image_tag)
        parser = RubocopParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
