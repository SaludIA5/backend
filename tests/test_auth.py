from datetime import timedelta

import pytest
from jose import jwt

from app.api.routes.auth import create_access_token
from app.core.config import settings
from app.databases.postgresql.models import User

BASE = "/auth"


# ---------- Helpers ----------
async def seed_user(db_session, email="user@example.com", password="secret123"):
    """Crea un usuario con password hasheado para test de login."""
    from passlib.hash import bcrypt

    hashed = bcrypt.hash(password)
    user = User(
        name="Tester",
        email=email,
        rut="11.111.111-1",
        hashed_password=hashed,
        is_doctor=True,
        is_chief_doctor=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ---------- TESTS ----------


@pytest.mark.asyncio
async def test_login_success_sets_cookie_and_returns_token(async_client, db_session):
    user = await seed_user(db_session)
    payload = {"email": user.email, "password": "secret123"}

    res = await async_client.post(f"{BASE}/login", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body

    # cookie debe existir
    cookies = res.cookies
    assert "access_token" in cookies
    token = body["access_token"]

    # decodificar y verificar claim
    decoded = jwt.decode(
        token,
        settings.security_config.secret_key,
        algorithms=[settings.security_config.algorithm],
    )
    assert decoded["sub"] == str(user.id)
    assert decoded["is_doctor"] is True
    assert decoded["is_chief_doctor"] is False


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client, db_session):
    user = await seed_user(db_session)
    # password incorrecto
    payload = {"email": user.email, "password": "wrong"}
    res = await async_client.post(f"{BASE}/login", json=payload)
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_user_not_found(async_client):
    payload = {"email": "no@ex.com", "password": "whatever"}
    res = await async_client.post(f"{BASE}/login", json=payload)
    assert res.status_code == 401
    assert "Invalid credentials" in res.json()["detail"]


@pytest.mark.asyncio
async def test_logout_deletes_cookie(async_client):
    res = await async_client.post(f"{BASE}/logout")
    assert res.status_code == 204
    # la cookie debe haber sido eliminada
    cookies = res.cookies
    assert "access_token" not in cookies


def test_create_access_token_expiration():
    """Valida creación manual de token y expiración custom."""
    token = create_access_token(
        subject="123",
        expires_delta=timedelta(minutes=5),
        is_doctor=True,
        is_chief_doctor=False,
    )
    decoded = jwt.decode(
        token,
        settings.security_config.secret_key,
        algorithms=[settings.security_config.algorithm],
    )
    assert decoded["sub"] == "123"
    assert decoded["is_doctor"] is True
    assert "exp" in decoded
