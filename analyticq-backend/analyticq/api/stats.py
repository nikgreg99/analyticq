import logging

from analyticq.repository.stats_repository import AnalyticQStatsRepository
from analyticq.service.stats_service import (AnalyticQStatsModel,
                                             AnalyticQStatsService)
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

stats_router = APIRouter(prefix="/stats", tags=["Stats Management"])


class ErrorResponse(BaseModel):
    detail: str


def get_stats_service(
    repo: AnalyticQStatsRepository = Depends(AnalyticQStatsRepository)
) -> AnalyticQStatsService:
    """Dependency provider for stats service."""
    return AnalyticQStatsService(repo)


@stats_router.get(
    "/{stats_id}",
    response_model=AnalyticQStatsModel,
    summary="Get stats analysis by ID",
    responses={
        status.HTTP_200_OK: {"description": "Ststs analysis details"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Analysis not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_stats(
    stats_id: int,
    stats_service: AnalyticQStatsService = Depends(get_stats_service),
):
    """
    Retrieve preanalysis statistics by its ID.

    - **stats_id**: ID of the preanalysis stats to retrieve.
    - **returns**: Preanalysis statistics data.
    """
    return await stats_service.get_stats(stats_id)


@stats_router.get(
    "/{stats_id}/context",
    summary="Get context by stats ID",
    responses={
        status.HTTP_200_OK: {"description": "Associated context details"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Context not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def context_by_stats_id(
    stats_id: int,
    stats_service: AnalyticQStatsService = Depends(get_stats_service),
):
    """
    Retrieve context associated with a specific stats ID.

    - **stats_id**: ID of the stats to retrieve context for.
    - **returns**: Context details associated with the stats.
    """
    return await stats_service.get_context_by_stats_id(stats_id)


@stats_router.delete(
    "/{stats_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete stats by ID",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Stats successfully deleted"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Stats not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_stats(
    stats_id: int,
    stats_service: AnalyticQStatsService = Depends(get_stats_service),
):
    """
    Delete preanalysis statistics by its ID.

    - **stats_id**: ID of the stats to delete.
    - **returns**: No content on successful deletion.
    """
    await stats_service.delete_stats(stats_id)
