from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import PHPStanAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import PHPStanParser
from analyticq.manager import AnalyticQContainerManager


class PHPStanTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "phpstan"
        image_tag = "latest"
        analyzer = PHPStanAnalyzer(container_manager, image_name, image_tag)
        parser = PHPStanParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
