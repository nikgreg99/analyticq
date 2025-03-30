from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import PylintAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import PylintParser
from analyticq.manager import AnalyticQContainerManager


class PylintTool(AnalyticQSASTTool):
    """A tool for analyzing Python code using Pylint.
    This tool integrates Pylint static code analyzer into the AnalyticQ framework.
    It uses a containerized environment to run Pylint analysis on Python source code.
    Attributes:
        supported_languages (set): Set containing "python" as the only supported language.
    Note:
        - Pylint official repository: https://github.com/pylint-dev/pylint
    Example:
        >>> pylint_tool = PylintTool()
        >>> results = pylint_tool.analyze(source_code)
    """

    supported_languages = {"python"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )
        image_name = "pylint"
        image_tag = "latest"
        analyzer = PylintAnalyzer(container_manager, image_name, image_tag)
        parser = PylintParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
