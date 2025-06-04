import logging
from tempfile import mkdtemp
from typing import Dict, List, Optional

from analyticq.manager.tool_manager import AnalyticQSASTManager
from analyticq.validator.analysis import AnalysisStatus

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service class for handling analysis operations."""

    def __init__(self, tracker):
        self.tracker = tracker
        self.sast_manager = AnalyticQSASTManager()

    async def analyze_git_repository(
        self,
        analysis_id: str,
        git_url: str,
        branch: Optional[str] = None,
        config_paths: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ):
        """Analyze a Git repository."""
        try:
            logger.info(f"[{analysis_id}] Starting Git analysis for {git_url}")
            self.tracker.update_status(analysis_id, AnalysisStatus.RUNNING)

            result = await self.sast_manager.scan_codebase(
                codebase_path=git_url,
                config_paths=config_paths,
                timeout=timeout,
                branch=branch or "main"
            )

            self.tracker.update_status(
                analysis_id,
                AnalysisStatus.COMPLETED,
                results=result,
                error=None
            )

            logger.info(f"[{analysis_id}] Git analysis completed successfully")

        except Exception as e:
            logger.error(f"[{analysis_id}] Git analysis failed: {e}")
            self.tracker.update_status(
                analysis_id,
                AnalysisStatus.FAILED,
                error=str(e),
                results=None
            )

    async def analyze_files(
        self,
        analysis_id: str,
        file_paths: List[str],
        config_paths: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        original_filenames: Optional[List[str]] = None
    ):
        """Analyze uploaded files."""
        record = self.tracker.get_analysis(analysis_id)
        if not record:
            logger.error(f"Analysis record not found: {analysis_id}")
            return

        temp_dir = None
        try:
            logger.info(f"[{analysis_id}] Starting file analysis")
            self.tracker.update_status(analysis_id, AnalysisStatus.RUNNING)

            # Create temporary directory
            temp_dir = mkdtemp(prefix=f"analysis_{analysis_id}_")
            self.tracker.update_status(analysis_id, AnalysisStatus.RUNNING, temp_dir=temp_dir)

            result = await self.sast_manager.scan_codebase(
                codebase_path=file_paths[0],  # Assuming first file is the main entry point
                config_paths=config_paths,
                timeout=timeout,
                original_path=original_filenames
            )

            self.tracker.update_status(
                analysis_id,
                AnalysisStatus.COMPLETED,
                results=result,
                error=None
            )

            logger.info(f"[{analysis_id}] File analysis completed successfully")

        except Exception as e:
            logger.error(f"[{analysis_id}] File analysis failed: {e}")
            self.tracker.update_status(
                analysis_id,
                AnalysisStatus.FAILED,
                error=str(e),
                results=None
            )
