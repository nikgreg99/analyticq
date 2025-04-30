import json
import logging
import os
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional
from uuid import uuid4

from analyticq.manager.tool_manager import AnalyticQSASTManager
from analyticq.schemas.analyse_dto import AnalysisResponse, GitRepoRequest
from fastapi import (APIRouter, BackgroundTasks, File, Form, HTTPException,
                     UploadFile)

logger = logging.getLogger(__name__)
analyze_router = APIRouter(prefix="/analyze", tags=["Analysis"])
sast_manager = AnalyticQSASTManager()

# In-memory analysis tracking (consider replacing with persistent storage in production)
analysis_results = {}


async def _run_git_analysis(
    analysis_id: str,
    git_url: str,
    branch: Optional[str] = None,
    config_paths: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None
):
    """Asynchronous task to analyze a Git repository."""
    try:
        logger.info(f"[{analysis_id}] Starting Git analysis for {git_url}")
        analysis_results[analysis_id]["status"] = "running"

        result = await sast_manager.scan_codebase(
            codebase_path=git_url,
            config_paths=config_paths,
            timeout=timeout,
            branch=branch or "main"
        )

        analysis_results[analysis_id] = {
            "analysis_id": analysis_id,
            "status": "completed",
            "results": result
        }

    except Exception as e:
        logger.error(f"[{analysis_id}] Git analysis failed: {str(e)}")
        analysis_results[analysis_id] = {
            "status": "failed",
            "error": str(e)
        }


async def _run_file_analysis(
    analysis_id: str,
    file_paths: List[str],
    config_paths: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    original_filenames: Optional[List[str]] = None
):
    """Asynchronous task to analyze uploaded files."""
    try:
        logger.info(f"[{analysis_id}] Starting file analysis")
        analysis_results[analysis_id]["status"] = "running"
        logger.info(f"[{analysis_id}] File paths: {file_paths}")
        result = await sast_manager.scan_codebase(
            codebase_path=file_paths,
            config_paths=config_paths,
            timeout=timeout,
            original_path=original_filenames
        )

        analysis_results[analysis_id] = {
            "analysis_id": analysis_id,
            "status": "completed",
            "results": result
        }

    except Exception as e:
        logger.error(f"[{analysis_id}] File analysis failed: {str(e)}")
        analysis_results[analysis_id] = {
            "status": "failed",
            "error": str(e)
        }


@analyze_router.post("/git", response_model=AnalysisResponse)
async def analyze_git_repo(
    background_tasks: BackgroundTasks,
    repo_request: GitRepoRequest,
):
    """Initiate analysis on a Git repository."""
    try:
        analysis_id = str(uuid4())
        analysis_results[analysis_id] = {"status": "pending"}

        background_tasks.add_task(
            _run_git_analysis,
            analysis_id,
            repo_request.git_url,
            repo_request.branch,
            repo_request.config_paths,
            repo_request.timeout
        )

        return AnalysisResponse(analysis_id=analysis_id, status="pending")

    except Exception as e:
        logger.error(f"Error initiating Git analysis: {str(e)}")
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
        analysis_id = str(uuid4())
        analysis_results[analysis_id] = {"status": "pending"}

        config_dict = {}
        if config_paths:
            try:
                config_dict = json.loads(config_paths)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid config_paths JSON format")

        temp_file_paths = []
        original_filenames = []

        for upload_file in files:
            if not any(upload_file.filename.endswith(ext) for ext in ['.zip', '.tar', '.gz']):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {upload_file.filename}"
                )

            with NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload_file.filename)[1]) as temp_file:
                temp_file.write(await upload_file.read())
                temp_file_paths.append(temp_file.name)
                original_filenames.append(upload_file.filename)
                logger.info(upload_file.filename)

                background_tasks.add_task(
                    _run_file_analysis,
                    analysis_id,
                    temp_file_paths[0],
                    config_dict,
                    timeout,
                    original_filenames[0]
                )

        return AnalysisResponse(analysis_id=analysis_id, status="pending")

    except Exception as e:
        logger.error(f"Error initiating file analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@analyze_router.get("/status/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_status(analysis_id: str):
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis ID not found")

    return AnalysisResponse(analysis_id=analysis_id, status=analysis_results[analysis_id]["status"])
