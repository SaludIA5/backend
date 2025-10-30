import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import User
from app.repositories.user import UserRepository

BASE = "/users"


# ---------- helpers ----------
async def seed_user(
    db: AsyncSession,
    *,
    name="User",
    email="user@example.com",
    rut="12.345.678-9",
    password="ChangeMe123!",
    is_doctor=False,
    is_chief_doctor=False,
    turn=None,
) -> User:
    return await UserRepository.create(
        db,
        name=name,
        email=email,
        rut=rut,
        password=password,
        is_doctor=is_doctor,
        is_chief_doctor=is_chief_doctor,
        turn=turn,
    )


# ---------- SIGNUP ----------
@pytest.mark.asyncio
async def test_signup_201_forces_roles_false(async_client, db_session: AsyncSession):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "rut": "10.111.111-1",
        "password": "ChangeMe123!",
        "turn": "A",
    }
    r = await async_client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Alice"
    # el endpoint fuerza roles en False:
    assert data.get("is_doctor") is False
    assert data.get("is_chief_doctor") is False
    # turn se respeta si viene
    assert data.get("turn") == "A"

    # en DB existe
    row = await db_session.get(User, data["id"])
    assert row and row.email == "alice@example.com"


@pytest.mark.asyncio
async def test_signup_409_email_duplicate(async_client, db_session: AsyncSession):
    await seed_user(db_session, name="Bob", email="dup@example.com", rut="20.222.222-2")
    r = await async_client.post(
        f"{BASE}/",
        json={
            "name": "Other",
            "email": "dup@example.com",
            "rut": "21.222.222-2",
            "password": "ChangeMe123!",
        },
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "Email ya registrado"


# ---------- LIST (login requerido) ----------
@pytest.mark.asyncio
async def test_list_users_pagination_and_search(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    # requiere login
    auth_user_manager_safe(doctor_user, is_doctor=True)

    await seed_user(db_session, name="Ana", email="ana@ex.com", rut="11.111.111-1")
    await seed_user(db_session, name="Beto", email="beto@ex.com", rut="22.222.222-2")
    await seed_user(db_session, name="Carla", email="carla@ex.com", rut="33.333.333-3")

    # paginación
    r = await async_client.get(f"{BASE}/", params={"page": 2, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["page"] == 2
    assert body["meta"]["page_size"] == 2
    assert body["meta"]["total_items"] >= 3
    assert len(body["items"]) <= 2

    # búsqueda
    r2 = await async_client.get(f"{BASE}/", params={"search": "Car"})
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert any(u["name"] == "Carla" for u in items)


# ---------- GET by ID (login requerido) ----------
@pytest.mark.asyncio
async def test_get_user_200(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user)
    u = await seed_user(db_session, name="Zoe", email="zoe@ex.com", rut="44.444.444-4")
    r = await async_client.get(f"{BASE}/{u.id}")
    assert r.status_code == 200
    assert r.json()["email"] == "zoe@ex.com"


@pytest.mark.asyncio
async def test_get_user_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user)
    r = await async_client.get(f"{BASE}/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


# ---------- GET by email (login requerido) ----------
@pytest.mark.asyncio
async def test_get_user_by_email_200(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user)
    u = await seed_user(
        db_session, name="Mail", email="mail@ex.com", rut="55.555.555-5"
    )
    r = await async_client.get(f"{BASE}/by-email/{u.email}")
    assert r.status_code == 200
    assert r.json()["id"] == u.id


@pytest.mark.asyncio
async def test_get_user_by_email_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user)
    r = await async_client.get(f"{BASE}/by-email/notfound@ex.com")
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


# ---------- UPDATE (solo admin) ----------
@pytest.mark.asyncio
async def test_update_user_200(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_admin=True)
    u = await seed_user(
        db_session,
        name="Old",
        email="old@ex.com",
        rut="66.666.666-6",
        turn=None,
        is_doctor=False,
    )

    r = await async_client.patch(
        f"{BASE}/{u.id}",
        json={"name": "New Name", "turn": "B", "is_doctor": True},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "New Name"
    assert data["turn"] == "B"
    assert data["is_doctor"] is True

    row = await db_session.get(User, u.id)
    assert row.name == "New Name" and row.turn == "B" and row.is_doctor is True


@pytest.mark.asyncio
async def test_update_user_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_admin=True)
    r = await async_client.patch(f"{BASE}/123456", json={"name": "X"})
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_update_user_409_email_duplicate(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_admin=True)

    # u1 = await seed_user(db_session, name="A", email="a@ex.com", rut="77.777.777-7")
    await seed_user(db_session, name="A", email="a@ex.com", rut="77.777.777-7")
    u2 = await seed_user(db_session, name="B", email="b@ex.com", rut="88.888.888-8")

    r = await async_client.patch(f"{BASE}/{u2.id}", json={"email": "a@ex.com"})
    assert r.status_code == 409
    assert r.json()["detail"] == "Email ya registrado"


@pytest.mark.asyncio
async def test_delete_user_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_admin=True)
    r = await async_client.delete(f"{BASE}/404")
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


# ---------- BY TURN (según implementación actual NO exige login en el código) ----------
@pytest.mark.asyncio
async def test_users_by_turn_groups(async_client, db_session: AsyncSession):
    # seed: A (doctor + chief), B (doctor), sin turno (chief sin turno)
    u1 = await seed_user(
        db_session,
        name="DocA",
        email="docA@ex.com",
        rut="1-9",
        is_doctor=True,
        turn="A",
    )
    u2 = await seed_user(
        db_session,
        name="ChiefA",
        email="chiefA@ex.com",
        rut="2-9",
        is_chief_doctor=True,
        turn="A",
    )
    u3 = await seed_user(
        db_session,
        name="DocB",
        email="docB@ex.com",
        rut="3-9",
        is_doctor=True,
        turn="B",
    )
    await seed_user(
        db_session,
        name="ChiefNil",
        email="chiefNil@ex.com",
        rut="4-9",
        is_chief_doctor=True,
        turn=None,
    )

    r = await async_client.get(f"{BASE}/by-turn")
    assert r.status_code == 200
    body = r.json()

    # claves esperadas (la ruta mapea cualquier turno fuera de A/B/C a "Sin turno")
    assert "A" in body and "B" in body and "Sin turno" in body

    ids_A = {u["id"] for u in body["A"]}
    ids_B = {u["id"] for u in body["B"]}
    ids_nil = {u["id"] for u in body["Sin turno"]}

    assert u1.id in ids_A and u2.id in ids_A
    assert u3.id in ids_B
    # el jefe sin turno debería aparecer en "Sin turno"
    assert any(u["is_chief_doctor"] for u in body["Sin turno"])
    assert len(ids_nil) >= 1
