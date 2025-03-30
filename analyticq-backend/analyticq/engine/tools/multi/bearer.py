from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import BearerAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import BearerParser
from analyticq.manager import AnalyticQContainerManager


class BearerTool(AnalyticQSASTTool):
    """
    A tool for analyzing code using the Bearer security scanner.
    This tool extends AnalyticQSASTTool to provide security scanning capabilities using Bearer.
    Bearer is an open source scanning tool that helps identify and address security and privacy
    issues in code.
    Attributes:
        supported_languages (set): Set of programming languages supported by Bearer scanner.
            Includes: go, java, js, typescript, ruby, php, python, ruby.
    Note:
        - Bearer official repository:  https://github.com/Bearer/bearer
    Example:
        ```python
        bearer_tool = BearerTool()
        results = bearer_tool.analyze("path/to/code")
        ```
    Notes:
        - Uses Bearer's container image for analysis
        - Runs in host network mode for container networking
    """

    supported_languages = {"go", "java", "js", "typescript", "ruby", "php", "python", "ruby"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "bearer"
        image_tag = "latest"
        container_manager.runtime_config.network.mode = "host"
        analyzer = BearerAnalyzer(container_manager, image_name, image_tag)
        parser = BearerParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
