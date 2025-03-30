from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import CheckStyleAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import CheckStyleParser
from analyticq.manager import AnalyticQContainerManager


class CheckstyleTool(AnalyticQSASTTool):
    """A tool class for running Checkstyle static analysis on Java code.
    Checkstyle is a development tool to help programmers write Java code that adheres to a coding standard.
    This class sets up and configures the Checkstyle analyzer to run in a containerized environment.
    Attributes:
        supported_languages (set): Set containing "java" as the only supported language.
    Note:
       - Checkcstyle official repository: https://github.com/checkstyle/checkstyle
    """

    supported_languages = {"java"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "checkstyle"
        # Need connection for downloading default XML config for making analysis
        container_manager.runtime_config.network.mode = "host"
        image_tag = "latest"
        analyzer = CheckStyleAnalyzer(container_manager, image_name, image_tag)
        parser = CheckStyleParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
