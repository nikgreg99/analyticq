
import logging

from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import PylintAnalyzer
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import PylintParser
from analyticq.manager import AnalyticQContainerManager

logger = logging.getLogger(__name__)


class PylintTool(AnalyticQSASTTool):

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
