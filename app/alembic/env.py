import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# --- Asegurar que el proyecto se encuentre en el path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from app.core.config import settings
from app.databases.postgresql.base import Base

# --- Configuración base de Alembic ---
config = context.config

# La URL ya viene correctamente formateada desde settings
db_url = settings.database_postgresql_url
print(
    f"[ALEMBIC] Using database URL: {db_url.split('@')[0]}@***"
)  # Mostrar sin password
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta las migraciones en modo 'offline' (sin conexión a la DB)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online_async() -> None:
    """Ejecuta las migraciones con conexión asíncrona."""
    connectable: AsyncEngine = create_async_engine(
        db_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Wrapper síncrono para ejecutar el loop async."""
    asyncio.run(run_migrations_online_async())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
