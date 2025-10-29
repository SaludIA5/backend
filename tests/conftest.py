"""Configuración global de pytest y fixtures preparadas para testing."""

import asyncio
import os
import random
from typing import AsyncGenerator, Generator, Callable, Awaitable
from types import SimpleNamespace
import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import inspect

from app.databases.postgresql.base import Base
from app.databases.postgresql.db import get_db
from app.repositories.user import UserRepository
from app.services.auth_service import get_current_user
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

# NUEVO: sessionmaker que NO expira atributos al hacer commit
TestSessionLocalNoExpire = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession, expire_on_commit=False
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


@pytest_asyncio.fixture(scope="function")
async def create_user(db_session: AsyncSession):
    """
    Factory async para crear usuarios con roles específicos usando el repositorio.
    """
    async def _create(
        *,
        name: str,
        email: str,
        rut: str,
        password: str = "ChangeMe123!",
        is_doctor: bool = False,
        is_chief_doctor: bool = False,
        turn: str | None = None,
    ):
        return await UserRepository.create(
            db_session,
            name=name,
            email=email,
            rut=rut,
            password=password,
            is_doctor=is_doctor,
            is_chief_doctor=is_chief_doctor,
            turn=turn,
        )
    return _create


@pytest_asyncio.fixture(scope="function")
async def doctor_user(create_user):
    """Crea y retorna un usuario con rol médico (turno A)."""
    return await create_user(
        name="Dr Test",
        email="dr.test@example.com",
        rut="12345678K",
        is_doctor=True,
        is_chief_doctor=False,
        turn="A",
    )


@pytest_asyncio.fixture(scope="function")
async def chief_user(create_user):
    """Crea y retorna un usuario con rol jefe médico (turno A)."""
    return await create_user(
        name="Chief Test",
        email="chief.test@example.com",
        rut="87654321K",
        is_doctor=False,
        is_chief_doctor=True,
        turn="A",
    )


@pytest.fixture(scope="function")
def auth_user_manager_safe(request):
    def _set(user, **overrides):
        pk = None
        try:
            insp = inspect(user)
            if insp.identity:
                pk = insp.identity[0]
        except Exception:
            pk = getattr(user, "id", None)

        safe_user = SimpleNamespace(
            id=int(pk) if pk is not None else None,
            email=overrides.get("email"),
            is_doctor=bool(overrides.get("is_doctor", False)),
            is_chief_doctor=bool(overrides.get("is_chief_doctor", overrides.get("is_chief", False))),
            is_admin=bool(overrides.get("is_admin", False)),
            turn=overrides.get("turn"),
            name=overrides.get("name"),
        )

        def _override():
            return safe_user

        app.dependency_overrides[get_current_user] = _override
        return safe_user

    def _finalize():
        app.dependency_overrides.pop(get_current_user, None)

    request.addfinalizer(_finalize)
    return _set


@pytest_asyncio.fixture(scope="function")
async def async_client_isolated(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Cliente async que usa una nueva AsyncSession por request para evitar transacciones anidadas."""
    from httpx import ASGITransport

    async def override_get_db():
        async with TestSessionLocalNoExpire() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def make_patient_isolated(async_client_isolated: AsyncClient):
    async def _create(headers: dict | None = None) -> int:
        rut = f"{random.randint(5_000_000, 25_000_000)}-{random.choice('0123456789K')}"
        payload = {"name": "John Lennon", "rut": rut, "age": 45}
        res = await async_client_isolated.post("/patients/", json=payload, headers=headers or {})
        assert res.status_code == 201, res.text
        return res.json()["id"]
    return _create


@pytest_asyncio.fixture(scope="function")
async def make_episode_isolated(async_client_isolated: AsyncClient):
    async def _create(patient_id: int, headers: dict | None = None) -> int:
        payload = {
            "patient_id": patient_id,
            "tipo": "SIN ALERTA",
            "triage": 3,
            "numero_episodio": f"test-{uuid.uuid4().hex[:8]}",
        }
        res = await async_client_isolated.post("/episodes/", json=payload, headers=headers or {})
        assert res.status_code == 201, res.text
        return res.json()["id"]
    return _create


@pytest_asyncio.fixture(scope="function")
async def set_ai_recommendation_isolated(async_client_isolated: AsyncClient):
    """Setea recomendación de IA vía /predictions/ usando el usuario autenticado actual."""
    async def _set(episode_id: int, headers: dict | None = None):
        payload = {
            "model_type": "random_forest",
            "id_episodio": episode_id,
            "tipo": "SIN ALERTA",
            "tipo_alerta_ugcc": "SIN ALERTA",
            "triage": 3,
            "presion_sistolica": 120,
            "presion_diastolica": 80,
        }
        res = await async_client_isolated.post("/predictions/", json=payload, headers=headers or {})
        assert res.status_code in (200, 201), res.text
    return _set