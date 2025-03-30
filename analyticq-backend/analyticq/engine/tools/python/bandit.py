from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import BanditAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import BanditParser
from analyticq.manager import AnalyticQContainerManager


class BanditTool(AnalyticQSASTTool):
    """A SAST (Static Application Security Testing) tool class that uses Bandit for Python code analysis.

    This tool integrates Bandit, a security linting tool specifically designed for Python code,
    into the AnalyticQ framework. It performs static security analysis on Python source code
    to identify common security issues and vulnerabilities.

    Attributes:
        supported_languages (set): A set containing "python" as the only supported language.

    Note:
        - Bandit official repository: https://github.com/PyCQA/bandit

    Example:
        tool = BanditTool()
        results = tool.analyze(source_code)
    """

    supported_languages = {"python"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "bandit"
        image_tag = "latest"
        analyzer = BanditAnalyzer(container_manager, image_name, image_tag)
        parser = BanditParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
