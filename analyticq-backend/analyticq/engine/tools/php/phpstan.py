from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import PHPStanAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import PHPStanParser
from analyticq.manager import AnalyticQContainerManager


class PhpstanTool(AnalyticQSASTTool):
    """PhpstanTool is a SAST (Static Application Security Testing) tool implementation for PHP code analysis.
    This class extends AnalyticQSASTTool and provides PHPStan static analysis capabilities through Docker
    containerization.
    Attributes:
        supported_languages (set): A set containing "php" as the only supported language
    Note:
        PHPStan official repository: https://github.com/phpstan/phpstan
    Example:
        tool = PhpstanTool()
        results = tool.analyze(source_code)
    """

    supported_languages = {"php"}

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )

        image_name = "phpstan"
        image_tag = "latest"
        analyzer = PHPStanAnalyzer(container_manager, image_name, image_tag)
        parser = PHPStanParser()
        super().__init__(analyzer, parser, container_manager, image_name, image_tag)
