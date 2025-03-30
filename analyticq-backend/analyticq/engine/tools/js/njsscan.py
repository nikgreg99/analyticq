from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import NjsScanAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import NjsScanParser
from analyticq.manager import AnalyticQContainerManager


class NjsscanTool(AnalyticQSASTTool):
    """
    A SAST tool for analyzing JavaScript code using NJSScan.
    This class extends AnalyticQSASTTool to provide JavaScript code analysis capabilities
    using the NJSScan static code analyzer. NJSScan is specifically designed to identify
    security vulnerabilities in Node.js applications.
    Attributes:
        supported_languages (set): A set containing "js" as the supported language.
    Note:
        Njjscan official repository: https://github.com/ajinabraham/njsscan
    Example:
        ```python
        tool = NjsscanTool()
        results = tool.analyze(source_code)
        ```
    """

    supported_languages = {"js"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "njsscan"
        image_tag = "latest"
        analyzer = NjsScanAnalyzer(container_manager, image_name, image_tag)
        parser = NjsScanParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
