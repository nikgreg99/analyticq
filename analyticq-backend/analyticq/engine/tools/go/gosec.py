from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import GoSecAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import GoSecParser
from analyticq.manager import AnalyticQContainerManager


class GosecTool(AnalyticQSASTTool):
    """
    A SAST tool implementation for analyzing Go code using Gosec security scanner.
    This class extends AnalyticQSASTTool to provide Go-specific static security analysis
    capabilities using the Gosec container image.
    Attributes:
        supported_languages (set): Set containing "go" as the supported language.
    Notes:
        - Uses Gosec scanner (https://github.com/securego/gosec) as the underlying analyzer
        - Security options are configured to prevent privilege escalation
    Example:
        tool = GosecTool()
        # Use tool methods inherited from AnalyticQSASTTool for analysis
    """

    supported_languages = {"go"}

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
