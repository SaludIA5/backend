from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Engine y session maker se crean de forma lazy para evitar que se creen
# antes de que Alembic pueda configurar su propio entorno
_engine = None
_AsyncSessionLocal = None


def get_engine():
    """Obtiene o crea el engine de SQLAlchemy."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_postgresql_url, pool_pre_ping=True, echo=True
        )
    return _engine


def get_async_session_local():
    """Obtiene o crea el async session maker."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=get_engine(),
        )
    return _AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session_local()() as session:
        yield session
