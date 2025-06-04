import json
import logging
from typing import List, Optional

from analyticq.schemas.analyse_dto import AnalysisResponse, GitRepoRequest
from analyticq.validator.analysis import AnalysisStatus
from fastapi import (APIRouter, BackgroundTasks, File, Form, HTTPException,
                     UploadFile)

from .handler import FileHandler
from .service import AnalysisService
from .tracker import AnalysisTracker

logger = logging.getLogger(__name__)

# Initialize components
analysis_tracker = AnalysisTracker()
analysis_service = AnalysisService(analysis_tracker)
analyze_router = APIRouter(prefix="/analyze", tags=["Analysis"])


@analyze_router.post("/git", response_model=AnalysisResponse)
async def analyze_git_repo(
    background_tasks: BackgroundTasks,
    repo_request: GitRepoRequest,
):
    """Initiate analysis on a Git repository."""
    try:
        analysis_id = analysis_tracker.create_analysis(
            analysis_type="git",
            git_url=repo_request.git_url
        )

        background_tasks.add_task(
            analysis_service.analyze_git_repository,
            analysis_id,
            repo_request.git_url,
            repo_request.branch,
            repo_request.config_paths,
            repo_request.timeout
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            status=AnalysisStatus.PENDING
        )

    except Exception as e:
        logger.error(f"Error initiating Git analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analyze_router.post("/files", response_model=AnalysisResponse)
async def analyze_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    config_paths: Optional[str] = Form(None),
    timeout: Optional[int] = Form(None),
):
    """Initiate analysis on uploaded file archives."""
    try:
        logger.info(f"Received {len(files)} files for analysis")

        # Parse config paths
        config_dict = {}
        if config_paths:
            try:
                config_dict = json.loads(config_paths)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid config_paths JSON format"
                )

        # Create analysis record
        analysis_id = analysis_tracker.create_analysis(analysis_type="file")

        # Process uploaded files
        temp_file_paths, original_filenames = await FileHandler.process_uploaded_files(
            files, analysis_id, analysis_tracker
        )

        # Start background analysis
        background_tasks.add_task(
            analysis_service.analyze_files,
            analysis_id,
            temp_file_paths,
            config_dict,
            timeout,
            original_filenames[0]
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            status=AnalysisStatus.PENDING
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating file analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analyze_router.get("/status/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis."""
    record = analysis_tracker.get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis ID not found")

    return AnalysisResponse(
        analysis_id=analysis_id,
        status=record.status,
        results=record.results,
        error=record.error
    )
