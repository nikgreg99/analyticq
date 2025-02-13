import json
from pathlib import Path

from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import StaticCheckAnalyzer
from analyticq.engine.core import ProgressReporter
from analyticq.engine.core.models import AnalyticQSASTScanResult
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import StaticCheckParser
from analyticq.exception import ScanConfigurationException
from analyticq.manager import AnalyticQContainerManager


class StaticCheckTool(AnalyticQSASTTool):

    def __init__(self, container_manager, image_name, image_tag):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=[]
            )
        )
        image_name = "staticcheck"
        image_tag = "latest"
        self.parser = StaticCheckParser()
        self.analyzer = StaticCheckAnalyzer(container_manager, image_name, image_tag)
        self.progess_reporter = ProgressReporter()
        super().__init__(container_manager, image_name, image_tag)

    async def run_scan(
            self,
            codebase_path: str,
            config_path: str = None,
            timeout: int = None) -> AnalyticQSASTScanResult:
        try:
            code_path = Path(codebase_path)
            if not code_path.exists():
                raise ScanConfigurationException(f"Code path does not exist for StaticCheck: {code_path}")

            # Validate config
            if config_path:
                config_path = Path(config_path)
                if not config_path.exists():
                    raise ScanConfigurationException(f"Config file not found for StaticCheck: {config_path}")

            results = await self.analyzer.run_analysis(
                codebase_path=code_path,
                config_path=config_path,
                timeout=timeout
            )

            results = json.loads(results)
            return self.parser.parse_scan_result(results)

        except ValueError as e:
            raise ScanConfigurationException(f"Invalid configuration : {str(e)}") from e
