import asyncio
import os
from logging.config import fileConfig

from alembic import context
from analyticq.config.db_conf import Base
from analyticq.model import *  # noqa
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables
load_dotenv()

# Load Alembic configuration
config = context.config

# Set up logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Set metadata for autogeneration
target_metadata = Base.metadata

# Read database URL from environment
DATABASE_URL = os.getenv("ANALYTICQ_DB_URL")

if not DATABASE_URL:
    raise ValueError(" ANALYTICQ_DB_URL environment variable is not set!")

# Create an async engine
async_engine = create_async_engine(DATABASE_URL, echo=True)


def run_migrations_offline():
    """Run migrations in offline mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in async mode without triggering greenlet_spawn errors."""
    async with async_engine.begin() as conn:
        await conn.run_sync(do_run_migrations)


def do_run_migrations(sync_conn):
    """Run migrations in sync mode to avoid greenlet_spawn issues."""
    context.configure(connection=sync_conn, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    if not asyncio.get_event_loop().is_running():
        asyncio.run(run_migrations_online())
    else:
        asyncio.create_task(run_migrations_online())
