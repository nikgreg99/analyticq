from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import FlakeAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import FlakeParser
from analyticq.manager import AnalyticQContainerManager


class FlakeTool(AnalyticQSASTTool):
    """FlakeTool class for performing static analysis using Flake8.
    A tool class that leverages Flake8 for Python code analysis within a containerized environment.
    Inherits from AnalyticQSASTTool to provide static analysis capabilities.
    Attributes:
        supported_languages (set): Set containing "python" as the only supported language.
    Notes:
        - Configures container with 1GB memory limit
        - Implements security options for container isolation
        - Flake tool: https://github.com/PyCQA/flake8
    """

    supported_languages = {"python"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )
        image_name = "flake8"
        image_tag = "latest"
        analyzer = FlakeAnalyzer(container_manager, image_name, image_tag)
        parser = FlakeParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
