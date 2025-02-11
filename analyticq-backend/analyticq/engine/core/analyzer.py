from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class AnalyticQAnalyzer(ABC):

    @abstractmethod
    async def run_analysis(
        self,
        code_path: str,
        config_path: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronously runs code analysis on a given source code file.
        This method performs static code analysis based on configured rules and yields
        analysis results as they become available.
        Args:
            code_path (str): Path to the source code file to analyze
            config_path (Optional[str]): Path to custom configuration file. If None, default config is used.
            timeout (Optional[int]): Maximum time in seconds for analysis to complete. If None, no timeout is applied.
        Yields:
            str: Analysis results as they are generated
        Raises:
            FileNotFoundError: If code_path or config_path (if specified) does not exist
            AnalysisError: If analysis fails to complete successfully
            TimeoutError: If analysis exceeds specified timeout duration
        """
        pass
