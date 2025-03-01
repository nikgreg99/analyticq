from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import CppCheckAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import CppCheckParser
from analyticq.manager import AnalyticQContainerManager


class CppCheckTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "cppcheck"
        image_tag = "latest"
        analyzer = CppCheckAnalyzer(container_manager, image_name, image_tag)
        parser = CppCheckParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
