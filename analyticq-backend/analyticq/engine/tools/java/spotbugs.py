from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import SpotBugsAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import SpotBugsParser
from analyticq.manager import AnalyticQContainerManager


class SpotbugsTool(AnalyticQSASTTool):
    """SpotBugsTool is a SAST analysis tool for Java code using SpotBugs.
    This class extends AnalyticQSASTTool to provide static code analysis capabilities
    specifically for Java applications using the SpotBugs analyzer.
    Attributes:
        supported_languages (set): A set containing "java" as the only supported language.
    Example:
        tool = SpotbugsTool()
        results = tool.analyze(source_code_path)
    Notes:
        - Spotbugs official repository: https://spotbugs.github.io
    """

    supported_languages = {"java"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[],
            )
        )
        image_name = "spotbugs"
        image_tag = "latest"
        container_manager.runtime_config.network.mode = "host"
        analyzer = SpotBugsAnalyzer(container_manager, image_name, image_tag)
        parser = SpotBugsParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
