import logging
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from analyticq.preprocessing.metric import (CodebaseMetricsCalculator,
                                            CodebaseMetricsCollector,
                                            CodebaseMetricsReporter)
from analyticq.repository.context_repository import AnalyticQContextRepository
from analyticq.repository.stats_repository import AnalyticQStatsRepository
from analyticq.service import AnalyticQContextService, AnalyticQStatsService
from analyticq.util import BatchUtil, TimeTrackerUtils
from analyticq.validator.stats import AnalyticQStatsModel
from dependency_injector.wiring import inject

from .codebase_cloner import CodebaseCloner
from .codebase_lang_scanner import CodebaseLangScanner

logger = logging.getLogger(__name__)


class CodebasePreprocessor:
    """This class handles the initial processing of source code repositories, including cloning them and scanning
    their contents to gather language-specific information. This is the main entrypoint of the preprocessing module.
    Attributes:
        cloner (CodebaseCloner): Component responsible for cloning git repositories.
        language_scanner (CodebaseLangScanner): Component that analyzes codebase for language information.
    Example:
        preprocessor = CodebasePreprocessor()
        report = await preprocessor.preprocess_codebase(
            "https://github.com/user/repo",
            branch="main",
            ssh_key_path="/path/to/key"
        )
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs) -> "CodebasePreprocessor":
        with cls._lock:
            if cls._instance is None:
                _instance = super().__new__(cls)
        return _instance

    @inject
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.cloner = CodebaseCloner()
            self.language_scanner = CodebaseLangScanner(CodebaseMetricsReporter(CodebaseMetricsCollector(), CodebaseMetricsCalculator()), TimeTrackerUtils(), BatchUtil())
            self._initialized = True
            self.context_service = AnalyticQContextService(AnalyticQContextRepository())
            self.stats_service = AnalyticQStatsService(AnalyticQStatsRepository())

    async def save_stats_for_codebase(
            self,
            path: Path,
            **stats: Dict[str, str]
    ) -> None:
        try:
            if isinstance(path, str):
                repo_name = path
            else:
                repo_name = path.name
            logger.info(f"Stats saved for repository: {repo_name}")
            context = await self.context_service.get_context_by_repo_name(repo_name)
            context_id = context.id
            stats['context_id'] = context_id
            new_stats = AnalyticQStatsModel(**stats)
            await self.stats_service.create_stats(new_stats)
        except Exception as e:
            logger.error(f"Failed to save context for codebase at {path}: {str(e)}")

    async def preprocess_codebase(
            self,
            codebase_url: str,
            branch: Optional[str] = None,
            tag: Optional[str] = None,
            ssh_key_path: Optional[str] = None,
            original_path: Optional[str] = None) -> Dict:
        """
        Preprocesses a codebase by cloning it and scanning its contents for language information.

        Args:
            codebase_url (str): URL of the codebase repository to process
            branch (str, optional): Specific branch to clone. Defaults to None.
            tag (str, optional): Specific tag to clone. Defaults to None.
            ssh_key_path (str, optional): Path to SSH key for private repositories. Defaults to None.

        Returns:
            Dict: A report containing information about languages used in the codebase

        Raises:
            May raise exceptions from underlying clone and scan operations
        """
        self.language_scanner = CodebaseLangScanner(CodebaseMetricsReporter(CodebaseMetricsCollector(), CodebaseMetricsCalculator()), TimeTrackerUtils(), BatchUtil())
        codebase_info = {
            "branch": branch,
            "tag": tag,
            "ssh_key_path": ssh_key_path
        }
        try:
            logger.info("ORIGINAL PATH in preprocess codebase: %s", original_path)
            repo_path = await self.cloner.clone(codebase_url, original_path, **codebase_info)
            logger.info(f"Cloned repository to: {repo_path}")
            await self.language_scanner.scan_codebase(repo_path)
            stats = self.language_scanner.generate_codebase_report()
            if original_path is not None:
                repo_path = original_path
            await self.save_stats_for_codebase(repo_path, **stats)
            return stats
        except Exception as e:
            raise Exception(f"Failed to preprocess codebase: {e}")
