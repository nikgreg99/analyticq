# analysis_tracker.py
import logging
import os
import shutil
import time
from typing import Dict, Optional
from uuid import uuid4

from analyticq.validator.analysis import AnalysisRecord, AnalysisStatus

logger = logging.getLogger(__name__)


class AnalysisTracker:
    """Manages analysis tracking and cleanup."""

    def __init__(self, max_analyses: int = 100):
        self._analyses: Dict[str, AnalysisRecord] = {}
        self._max_analyses = max_analyses

    def create_analysis(self, analysis_type: str, **kwargs) -> str:
        """Create a new analysis record."""
        analysis_id = str(uuid4())
        self._analyses[analysis_id] = AnalysisRecord(
            analysis_id=analysis_id,
            status=AnalysisStatus.PENDING,
            created_at=time.time(),
            analysis_type=analysis_type,
            **kwargs
        )
        self._cleanup_old_analyses()
        return analysis_id

    def get_analysis(self, analysis_id: str) -> Optional[AnalysisRecord]:
        """Get analysis record by ID."""
        return self._analyses.get(analysis_id)

    def update_status(self, analysis_id: str, status: AnalysisStatus, **kwargs):
        """Update analysis status and optional fields."""
        if analysis_id in self._analyses:
            record = self._analyses[analysis_id]
            record.status = status
            for key, value in kwargs.items():
                setattr(record, key, value)

    def remove_analysis(self, analysis_id: str) -> Optional[AnalysisRecord]:
        """Remove and return analysis record."""
        return self._analyses.pop(analysis_id, None)

    def _cleanup_old_analyses(self):
        """Remove old completed/failed analyses to prevent memory buildup."""
        if len(self._analyses) <= self._max_analyses:
            return

        # Sort by creation time (oldest first)
        sorted_analyses = sorted(
            self._analyses.items(),
            key=lambda x: x[1].created_at
        )

        # Remove oldest completed/failed analyses
        to_remove = len(self._analyses) - self._max_analyses
        for analysis_id, record in sorted_analyses[:to_remove]:
            if record.status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
                self._cleanup_analysis_files(record)
                del self._analyses[analysis_id]

    def _cleanup_analysis_files(self, record: AnalysisRecord):
        """Clean up temporary files and directories for an analysis."""
        # Clean up temp files
        for temp_file in record.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Could not delete temp file {temp_file}: {e}")

        # Clean up temp directory
        if record.temp_dir and os.path.exists(record.temp_dir):
            try:
                shutil.rmtree(record.temp_dir)
            except Exception as e:
                logger.warning(f"Could not delete temp directory {record.temp_dir}: {e}")
