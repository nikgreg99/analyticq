from threading import Lock
from typing import Dict, Optional

from analyticq.preprocessing.metric import (CodebaseMetricsCalculator,
                                            CodebaseMetricsCollector,
                                            CodebaseMetricsReporter)
from analyticq.util import BatchUtil, TimeTrackerUtils
from dependency_injector.wiring import Provide, inject

from .codebase_cloner import CodebaseCloner
from .codebase_lang_scanner import CodebaseLangScanner


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
    def __init__(self,
                 cloner: Provide[CodebaseCloner] = None,
                 language_scanner: Provide[CodebaseLangScanner] = None):
        if not hasattr(self, "_initialized"):
            self.cloner = cloner or CodebaseCloner()
            self.language_scanner = language_scanner or CodebaseLangScanner(CodebaseMetricsReporter(CodebaseMetricsCollector(), CodebaseMetricsCalculator()), TimeTrackerUtils(), BatchUtil())
            self._initialized = True

    async def preprocess_codebase(
            self, codebase_url: str,
            branch: Optional[str] = None,
            tag: Optional[str] = None,
            ssh_key_path: Optional[str] = None) -> Dict:
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
        codebase_info = {
            "branch": branch,
            "tag": tag,
            "ssh_key_path": ssh_key_path
        }
        try:
            repo_path = await self.cloner.clone(codebase_url, **codebase_info)
            await self.language_scanner.scan_codebase(repo_path)
            return self.language_scanner.generate_codebase_report()
        except Exception as e:
            raise Exception(f"Failed to preprocess codebase: {e}")
