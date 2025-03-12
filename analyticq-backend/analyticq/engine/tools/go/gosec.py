from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import GoSecAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import GoSecParser
from analyticq.manager import AnalyticQContainerManager


class GoSecTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )
        image_name = "gosec"
        image_tag = "latest"
        analyzer = GoSecAnalyzer(container_manager, image_name, image_tag)
        parser = GoSecParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
