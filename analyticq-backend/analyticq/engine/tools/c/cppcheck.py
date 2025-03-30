from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import CppCheckAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import CppCheckParser
from analyticq.manager import AnalyticQContainerManager


class CppcheckTool(AnalyticQSASTTool):
    """A class representing a CppCheck static analysis tool integration for C/C++ code.
    This tool uses the CppCheck static analyzer to perform code analysis on C and C++
    source files within a containerized environment.
    Attributes:
        supported_languages (set): A set of programming languages supported by this tool,
            containing "c" and "c++".
    Notes:
        - Cppcheck official repository : https://github.com/danmar/cppcheck
    """

    supported_languages = {"c", "c++"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "cppcheck"
        image_tag = "latest"
        analyzer = CppCheckAnalyzer(container_manager, image_name, image_tag)
        parser = CppCheckParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
