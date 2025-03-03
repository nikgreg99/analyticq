from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import PyrightAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import PyrightParser
from analyticq.manager import AnalyticQContainerManager


class PyrightTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )
        image_name = "pyright"
        image_tag = "latest"
        analyzer = PyrightAnalyzer(container_manager, image_name, image_tag)
        parser = PyrightParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
