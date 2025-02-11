import logging
import os
from threading import Lock
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()


class AnalyticQDatabaseManager:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._engine = create_async_engine(
                os.environ.get("ANALYTICQ_DB_URL"),
                echo=True
            )
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            self.initialized = True

    async def init_db(self):
        """
        Initialize the database by creating all tables defined in SQLAlchemy models.

        This asynchronous method establishes a connection to the database using the engine
        and creates all tables that are defined in the SQLAlchemy Base metadata if they
        don't already exist.

        Returns:
            None

        Raises:
            SQLAlchemyError: If there is an error during database initialization
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Asynchronous database session generator.

        Creates and manages a database session using the AsyncSession factory. The session is
        automatically committed on successful operations and rolled back on exceptions.

        Yields:
            AsyncSession: An asynchronous SQLAlchemy session object.

        Raises:
            Exception: Any database-related exception that occurs during session operations.

        Note:
            The session is automatically closed in the finally block, ensuring proper resource cleanup
            even if an exception occurs.
        """
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"AnalyticQ Session error: {e}")
            raise
        finally:
            await session.close()

    async def close(self):
        """
        Closes the database connection and releases all resources.

        This method ensures proper cleanup of the SQLAlchemy engine by disposing
        all connection pools and releasing database resources.

        Returns:
            None

        Raises:
            SQLAlchemyError: If there is an error while closing the database connection.
        """
        await self._engine.dispose()
