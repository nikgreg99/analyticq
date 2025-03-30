from __future__ import annotations

from typing import Optional

from analyticq.manager import AnalyticQDatabaseManager
from analyticq.model.excluded_files import AnalyticQExcludedFiles
from analyticq.model.stats import AnalyticQStats
from analyticq.validator.context import AnalyticQContextModel
from analyticq.validator.stats import AnalyticQStatsModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import joinedload, selectinload


class AnalyticQStatsRepository:
    """"
    A repository class for managing statistics data in the AnalyticQ system.
    This class provides methods to perform CRUD operations (Create, Read, Update, Delete)
    on statistics data in the database.
    Methods:
        add_statistics(stats_data: AnalyticQStatsModel) -> AnalyticQStatsModel:
            Adds new statistics data to the database.
        get_stats_by_id(analysis_id: int) -> Optional[AnalyticQStatsModel]:
            Retrieves statistics analysis by ID.
        get_context_by_id(stats_id: int) -> Optional[AnalyticQContextModel]:
            Retrieves the context associated with a specific stats ID.
        update_stats(stats_id: int, **kwargs) -> AnalyticQStatsModel:
            Updates existing statistics data.
        delete_stats(stats_id: int) -> bool:
            Deletes statistics data from the database.
    """

    async def add_statistics(self, stats_data: AnalyticQStatsModel) -> AnalyticQStatsModel:
        """
        Adds statistics data to the database.

        Args:
            stats_data (AnalyticQStatsModel): The statistics data model to be inserted into the database.

        Returns:
            AnalyticQStatsModel: The newly created statistics data model after insertion.

        Raises:
            SQLAlchemyError: If there's an error during database operation.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stats_dict = stats_data.model_dump()

        # First create the excluded_files record if needed
            if 'excluded_files' in stats_dict:
                excluded_files_data = stats_dict.pop('excluded_files')
                stmt = insert(AnalyticQExcludedFiles).values(**excluded_files_data).returning(AnalyticQExcludedFiles)
                result = await session.execute(stmt)
                excluded_files = result.scalar_one()
                stats_dict['excluded_files_id'] = excluded_files.id

            stmt = insert(AnalyticQStats).values(**stats_dict).returning(AnalyticQStats)
            result = await session.execute(stmt)
            new_stats = result.scalar_one()

            await session.refresh(new_stats, ['excluded_files'])

        return AnalyticQStatsModel.model_validate(new_stats)

    async def get_stats_by_id(self, id: int) -> Optional["AnalyticQStatsModel"]:
        """
        Retrieve statistics analysis by its ID from the database.
        Args:
            analysis_id (int): The ID of the statistics analysis to retrieve.
        Returns:
            Optional[AnalyticQStatsModel]: The statistics analysis model if found, None otherwise.
        Raises:
            None
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            query = (
                select(AnalyticQStats)
                .options(
                    selectinload(AnalyticQStats.excluded_files),
                )
                .where(AnalyticQStats.id == id)
            )
            # Execute query with eager loading
            result = await session.execute(query)
            stats_record = result.scalar_one_or_none()
            if stats_record:
                await session.refresh(stats_record)
                return AnalyticQStatsModel.model_validate(stats_record)
            return None

    async def get_context_by_id(self, context_id: int) -> Optional[AnalyticQContextModel]:
        """
        Retrieve the context associated with a specific stats ID from the database.
        Args:
            context_id (int): The ID of the statistics analysis to fetch the context for.
        Returns:
            Optional[AnalyticQContextModel]: The context model if found, None otherwise.
        Notes:
            This method queries the database for a stats analysis entry matching the given ID
            and returns its associated context if it exists.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = (select(AnalyticQStats)
                    .options(joinedload(AnalyticQStats.context))
                    .where(AnalyticQStats.id == context_id)
                    )
            result = await session.execute(stmt)
            analysis = result.scalars().first()

            return AnalyticQContextModel.model_validate(analysis.context) if analysis else None

    async def update_stats(self, stats_id: int, stats_data: AnalyticQStatsModel) -> AnalyticQStatsModel:
        """"
            Update stats for a given s ID.
            Args:
                stats_id (int): The ID of the analysis to update
                **kwargs: Variable keyword arguments containing fields to update
            Returns:
                AnalyticQStatsModel: The updated statistics model object
            Raises:
                sqlalchemy.exc.NoResultFound: If no analysis found with given ID
                sqlalchemy.exc.MultipleResultsFound: If multiple analyses found with given ID
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stats_dict = stats_data.model_dump(exclude_unset=True)

            if "excluded_files" in stats_dict:
                excluded_files_data = stats_dict.pop("excluded_files")

                existing_stats = await session.get(AnalyticQStats, stats_id)

                if existing_stats and existing_stats.excluded_files_id:
                    update_stmt = update(AnalyticQExcludedFiles).where(
                        AnalyticQExcludedFiles.id == existing_stats.excluded_files_id
                    ).values(excluded_files_data).returning(AnalyticQExcludedFiles)
                    await session.execute(update_stmt)
                else:
                    excluded_dir_stmt = insert(AnalyticQExcludedFiles).values(excluded_files_data).returning(AnalyticQExcludedFiles)

                    result = await session.execute(excluded_dir_stmt)
                    excluded_files_data = result.scalar_one()
                    stats_dict["excluded_files_id"] = excluded_files_data.id

            stmt = update(AnalyticQStats).where(AnalyticQStats.id == stats_id).values(stats_dict).returning(AnalyticQStats)
            result = await session.execute(stmt)

            updated_stats = result.scalar_one()
            await session.refresh(updated_stats, ['excluded_files'])

        return AnalyticQStatsModel.model_validate(updated_stats)

    async def delete_stats(self, stats_id: int) -> bool:
        """
        Deletes a stats record from the database.

        Args:
            analysis_id (int): The ID of the stats to delete.

        Returns:
            bool: True if the analysis was successfully deleted, False if no matching record was found.

        Raises:
            SQLAlchemyError: If there is a database error during deletion.
        """
        async with AnalyticQDatabaseManager().get_db_session() as session:
            stmt = delete(AnalyticQStats).where(AnalyticQStats.id == stats_id)
            result = await session.execute(stmt)
            return result.rowcount > 0
