from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import FlawFinderAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import FlawFinderParser
from analyticq.manager import AnalyticQContainerManager


class FlawfinderTool(AnalyticQSASTTool):
    """FlawfinderTool is a SAST (Static Application Security Testing) tool wrapper for Flawfinder.
    This class provides functionality to analyze C/C++ source code for potential security flaws
    using the Flawfinder static analyzer. It inherits from AnalyticQSASTTool and configures
    the necessary container environment for running Flawfinder analyses.
    Attributes:
        supported_languages (set): A set of programming languages supported by this tool,
            specifically {"c", "c++"}.

    Note:
        - Flawfinder official repository: https://github.com/david-a-wheeler/flawfinder

    Example:
        tool = FlawfinderTool()
        # Use tool to analyze C/C++ code
    """

    supported_languages = {"c", "c++"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "flawfinder"
        image_tag = "latest"
        analyzer = FlawFinderAnalyzer(container_manager, image_name, image_tag)
        parser = FlawFinderParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
