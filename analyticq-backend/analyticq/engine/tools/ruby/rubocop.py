from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import RubocopAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import RubocopParser
from analyticq.manager import AnalyticQContainerManager


class RubocopTool(AnalyticQSASTTool):
    """A tool for analyzing Ruby code using Rubocop.
    This class extends AnalyticQSASTTool and provides functionality to analyze Ruby source code
    using the Rubocop static analyzer. It initializes with default container configurations and
    uses the official Rubocop Docker image.
    Attributes:
        supported_languages (set): A set containing "ruby" as the only supported language.
    Note:
        Rubocop official repository: https://github.com/rubocop/rubocop
    Example:
        tool = RubocopTool()
        results = tool.analyze(source_code)
    """

    supported_languages = {"ruby"}

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
