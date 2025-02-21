from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import StaticCheckAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import StaticCheckParser
from analyticq.manager import AnalyticQContainerManager


class StaticCheckTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )
        image_name = "staticcheck"
        image_tag = "latest"
        analyzer = StaticCheckAnalyzer(container_manager, image_name, image_tag)
        parser = StaticCheckParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
