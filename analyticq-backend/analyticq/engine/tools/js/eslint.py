from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import ESLintAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import ESLintParser
from analyticq.manager import AnalyticQContainerManager


class ESLintTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "eslint"
        image_tag = "latest"
        analyzer = ESLintAnalyzer(container_manager, image_name, image_tag)
        parser = ESLintParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
