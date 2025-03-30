from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import PyrightAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import PyrightParser
from analyticq.manager import AnalyticQContainerManager


class PyrightTool(AnalyticQSASTTool):
    """A tool for performing static analysis on Python code using Pyright.
    This class extends AnalyticQSASTTool to provide Python static type checking and analysis
    functionality using Microsoft's Pyright tool in a containerized environment.
    Attributes:
        supported_languages (set): A set containing only "python" as the supported language.
    Note:
        - Pyright official repository: https://github.com/microsoft/pyright
    Example:
        ```python
        tool = PyrightTool()
        results = tool.analyze(source_code)
        ```
    """

    supported_languages = {"python"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )
        image_name = "pyright"
        image_tag = "latest"
        analyzer = PyrightAnalyzer(container_manager, image_name, image_tag)
        parser = PyrightParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
