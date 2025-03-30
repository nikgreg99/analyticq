from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import StaticCheckAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import StaticCheckParser
from analyticq.manager import AnalyticQContainerManager


class StaticcheckTool(AnalyticQSASTTool):
    """
    A tool class that implements Staticcheck static analysis for Go programming language.
    This class extends AnalyticQSASTTool to provide static analysis capabilities specifically
    for Go code using the Staticcheck tool. It initializes with specific container runtime
    configurations and sets up the necessary analyzer and parser components.
    Attributes:
        supported_languages (set): A set containing "go" as the supported programming language.
    Note:
        - Staticcheck official repository: https://github.com/dominikh/go-tools
        - The tool runs with memory limit of 1GB and specific security options in a containerized
        environment.
    """

    supported_languages = {"go"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )
        image_name = "staticcheck"
        image_tag = "latest"
        analyzer = StaticCheckAnalyzer(container_manager, image_name, image_tag)
        parser = StaticCheckParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
