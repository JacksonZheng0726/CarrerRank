from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.models  # noqa: F401
from alembic import context
from app.core.config import get_settings
from app.core.platform import psycopg_compatible_loop_factory
from app.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

configured_url = config.get_main_option("sqlalchemy.url")
database_url = configured_url or get_settings().database_url
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
target_metadata = Base.metadata

"""
This file is run when Alembic runs. 
It loads the database URL and SQLAlchemy model metadata,
then applies or generates migrations.

"""

def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"connect_timeout": 5},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(
        run_async_migrations(),
        loop_factory=psycopg_compatible_loop_factory,
    )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
