import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()


class AnalyticQDatabaseManager:

    _instance: Optional["AnalyticQDatabaseManager"] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_engine()
            self._initialized = True

    def _get_databse_url(self) -> str:
        """
        Retrieves the database URL from environment variables.

        Returns:
            str: The database URL stored in 'ANALYTICQ_DB_URL' environment variable.
            None if the environment variable is not set.
        """
        return os.environ.get("ANALYTICQ_DB_URL")

    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine and session factory.

        This method sets up the database engine using the provided database URL and configures
        the session factory for database operations.

        Raises:
            ValueError: If database URL is not set in environment variables (ANALYTICQ_DB_URL)

        """
        db_url = self._get_databse_url()
        logger.info(f"Initializing database with URL: {db_url}")
        if not db_url:
            raise ValueError("Database URL not set in environment variables (ANALYTICQ_DB_URL)")

        # Set echo based on environment to avoid excessive logging in production
        echo = os.environ.get("ANALYTICQ_DB_ECHO", "false").lower() == "true"

        self._engine = create_async_engine(
            db_url,
            echo=echo,
            pool_pre_ping=True,
        )

        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

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
        if not self._engine:
            self._initialize_engine()
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @asynccontextmanager
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
        if not self._session_factory:
            self._initialize_engine()

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
        if self._engine:
            try:
                await self._engine.dispose()
                logger.info("Database connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
                raise
            finally:
                self._engine = None
                self._session_factory = None
