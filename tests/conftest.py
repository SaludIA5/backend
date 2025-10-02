"""Configuración global de pytest y fixtures preparadas para testing."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.databases.postgresql.db import Base, get_db
from app.main import app

# Configuración para base de datos de testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Crear motor de testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Crear un event loop para toda la sesión de testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Crear una sesión de base de datos para cada test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Crear cliente de testing con base de datos mock."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Crear cliente async para testing."""
    from httpx import ASGITransport

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Configurar variables de entorno para testing."""
    os.environ["BACKEND_APP_ENVIRONMENT"] = "testing"
    os.environ["BACKEND_APP_DEBUG"] = "true"
    yield
    if "BACKEND_APP_ENVIRONMENT" in os.environ:
        del os.environ["BACKEND_APP_ENVIRONMENT"]
    if "BACKEND_APP_DEBUG" in os.environ:
        del os.environ["BACKEND_APP_DEBUG"]
