import json
from pathlib import Path

from analyticq.config.models import AnalyticQContainerRuntimeConfig
from analyticq.engine.analyzer import BanditAnalyzer
from analyticq.engine.core import ProgressReporter
from analyticq.engine.core.models import AnalyticQSASTScanResult
from analyticq.engine.core.sast_tool import AnalyticQSASTTool
from analyticq.engine.parser import BanditResultParser
from analyticq.exception import ScanConfigurationException
from analyticq.manager import AnalyticQContainerManager


class BanditTool(AnalyticQSASTTool):

    def __init__(self):
        container_manager = AnalyticQContainerManager(
            runtime_config=AnalyticQContainerRuntimeConfig(
                memory="1g",
                security_opts=["no-new-privileges:true", "seccomp:unconfined"]
            )
        )

        image_name = "bandit"
        image_tag = "latest"
        super().__init__(container_manager, image_name, image_tag)
        self.analyzer = BanditAnalyzer(self.container_manager, self.image_name, self.image_tag)
        self.parser = BanditResultParser()
        self.progess_reporter = ProgressReporter()

        self.container_manager = container_manager
        self.image_name = image_name
        self.image_tag = image_tag

    async def run_scan(
            self,
            codebase_path: str,
            config_path: str = None,
            timeout: int = None) -> AnalyticQSASTScanResult:

        try:
            code_path = Path(codebase_path)
            if not code_path.exists():
                raise ScanConfigurationException(f"Code path does not exist: {code_path}")

            # Validate config
            if config_path:
                config_path = Path(config_path)
                if not config_path.exists():
                    raise ScanConfigurationException(f"Config file not found: {config_path}")

            results = await self.analyzer.run_analysis(
                codebase_path=code_path,
                config_path=config_path,
                timeout=timeout
            )

            results = json.loads(results)
            return self.parser.parse_scan_result(results)

        except ValueError as e:
            raise ScanConfigurationException(f"Invalid configuration : {str(e)}") from e
