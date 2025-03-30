import logging

from analyticq.repository.stats_repository import (AnalyticQContextModel,
                                                   AnalyticQStatsModel,
                                                   AnalyticQStatsRepository)
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AnalyticQStatsService:
    """
    A service class for managing statistical analysis data in AnalyticQ.
    This service provides methods for creating, retrieving, updating, and deleting statistical
    analysis records, as well as managing associated context data. It acts as an intermediary
    layer between the API controllers and the repository layer, handling business logic,
    error handling, and data validation.
    """

    def __init__(self, repo: AnalyticQStatsRepository):
        self.repo = repo

    async def create_stats(self, stats_data: AnalyticQStatsModel) -> AnalyticQStatsModel:
        """
        Creates and stores statistical analysis data in the repository.

        Args:
            stats_data (AnalyticQStatsModel): The statistical data to be stored.

        Returns:
            AnalyticQStatsModel: The created statistical analysis record.

        Raises:
            HTTPException: If validation fails (400) or if there are database/server errors (500).

        Note:
            This is an asynchronous function that handles the creation of preprocessing statistics,
            including error handling and logging.
        """
        try:
            stats = await self.repo.add_statistics(stats_data)
            if not stats:
                logger.error("Failed to retrieve created preprocessing analysis from the repository.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve created preprocessing analysis."
                )
            logger.info(f"Stats created successfully: {stats.id}")
            return stats
        except ValueError as e:
            logger.error(f"Validation error while creating preprocessing analysis: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error while creating preprocessing analysis: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the preprocessing analysis."
            )

    async def get_stats(self, stats_id: int) -> AnalyticQStatsModel:
        """
        Retrieve a statistic recoed by its ID.

        Args:
            stats_id (int): The ID of the preprocessing analysis to retrieve.

        Returns:
            AnalyticQStatsModel: The retrieved preprocessing analysis.

        Raises:
            HTTPException:
                - 404: If the analysis is not found.
                - 500: If there's an unexpected server error.
        """
        try:
            stats = await self.repo.get_stats_by_id(stats_id)
            if not stats:
                logger.error(f"Stats {stats_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stats {stats_id} not found."
                )
            return stats
        except Exception as e:
            logger.error(f"Unexpected error while retrieving stasts with ID {stats_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while retrieving the stats. {stats_id}"
            )

    async def get_context_by_stats_id(self, stats_id: int) -> AnalyticQContextModel:
        """
        Retrieves the context associated with a specific stats ID.

        Args:
            stats_id (int): The ID of the stats entry to get the context for.

        Returns:
            AnalyticQContextModel: The context model associated with the stats ID.

        Raises:
            HTTPException:
                - 404 if the context is not found for the given stats ID
                - 500 if an unexpected error occurs during retrieval
        """
        try:
            context = await self.repo.get_context_by_id(stats_id)
            if not context:
                logger.error(f"Context related to stats {stats_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Context related to stats {stats_id} not found."
                )
        except Exception as e:
            logger.error(f"Unexpected error while retrieving content related to stats with ID {stats_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while retrieving the stats. {stats_id}"
            )

    async def update_stats(self, stats_id: int, stats_data: AnalyticQStatsModel) -> AnalyticQStatsModel:
        """
        Updates statistics data for a given stats ID.

        Args:
            stats_id (int): The ID of the stats record to update
            stats_data (AnalyticQStatsModel): The new stats data to update with

        Returns:
            AnalyticQStatsModel: The updated stats record

        Raises:
            HTTPException: If stats with given ID is not found (404) or if there's an internal server error (500)
        """
        try:
            stats = await self.repo.update_stats(stats_id, stats_data)
            if not stats:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stats with ID {stats_id} not found "
                )
            logger.info(f"Stats updated successfully: {stats.id}")
            return stats
        except Exception as e:
            logger.error(f"An unexpected error occurred while retrieving the stats with ID {stats_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while retrieving the stats with ID {stats_id}"
            )

    async def delete_stats(self, stats_id: int) -> None:
        """
        Deletes a statistical record by its ID.

        This method attempts to delete statistical data from the repository using the provided stats_id.
        If the deletion is unsuccessful because the record doesn't exist, it raises a 404 HTTP exception.
        For any other errors during deletion, it raises a 500 HTTP exception.

        Args:
            stats_id (int): The unique identifier of the statistical record to be deleted.

        Raises:
            HTTPException:
                - HTTP 404 if the stats with the given ID is not found
                - HTTP 500 if there's an internal server error during deletion

        Returns:
            None
        """
        try:
            deleted = await self.repo.delete_stats(stats_id)
            if not deleted:
                logger.error(f"Stats {stats_id} not found during deletion.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stats with {stats_id} not found"
                )
            logger.info(f"Ststs deleted successfully: {stats_id}")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting stats {str(e)}"
            )
