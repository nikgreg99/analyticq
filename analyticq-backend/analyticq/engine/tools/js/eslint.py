from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import ESLintAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import ESLintParser
from analyticq.manager import AnalyticQContainerManager


class EslintTool(AnalyticQSASTTool):
    """ESLint static analysis tool implementation for JavaScript code.
    This class implements the ESLint static code analyzer as an AnalyticQ SAST tool.
    ESLint is a popular linter that helps identify and fix problems in JavaScript code.
    The tool runs ESLint in a containerized environment with specified memory limits
    and security options.
    Attributes:
        supported_languages (set): Set containing "js" as the supported language
    Args:
        None
    Notes:
        - Eslint official repository: https://github.com/eslint/eslint
    Example:
        ```python
        tool = EslintTool()
        results = tool.analyze(code="const x = 1;", filename="test.js")
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

        image_name = "eslint"
        image_tag = "latest"
        analyzer = ESLintAnalyzer(container_manager, image_name, image_tag)
        parser = ESLintParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
