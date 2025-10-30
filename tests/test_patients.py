# from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Patient
from app.repositories import PatientRepository

BASE = "/patients"


# ---------------------------
# Helpers para seeding rápido
# ---------------------------
async def seed_patient(db: AsyncSession, name="John Doe", rut="11.111.111-1", age=40):
    p = await PatientRepository.create(db, name=name, rut=rut, age=age)
    return p


# -------------
# CREATE (201/409)
# -------------
@pytest.mark.asyncio
async def test_create_patient_201(
    async_client, auth_user_manager_safe, doctor_user, db_session: AsyncSession
):
    auth_user_manager_safe(doctor_user, is_doctor=True)  # require_medical_role
    payload = {"name": "Jane Roe", "rut": "12.345.678-9", "age": 33}

    r = await async_client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Jane Roe"
    # verificación en DB
    row = await db_session.get(Patient, data["id"])
    assert row and row.rut == "12.345.678-9"


@pytest.mark.asyncio
async def test_create_patient_conflict_409(
    async_client, auth_user_manager_safe, doctor_user, db_session: AsyncSession
):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    await seed_patient(db_session, name="A", rut="22.222.222-2")
    r = await async_client.post(
        f"{BASE}/", json={"name": "B", "rut": "22.222.222-2", "age": 50}
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "RUT ya registrado"


# -----------------------
# LIST (paginación/search)
# -----------------------
@pytest.mark.asyncio
async def test_list_patients_pagination_and_search(
    async_client, auth_user_manager_safe, doctor_user, db_session: AsyncSession
):
    auth_user_manager_safe(doctor_user)  # requiere login
    # 6 pacientes
    await seed_patient(db_session, name="Alice", rut="10.000.000-1")
    await seed_patient(db_session, name="Bob", rut="10.000.000-2")
    await seed_patient(db_session, name="Charlie", rut="10.000.000-3")
    await seed_patient(db_session, name="David", rut="10.000.000-4")
    await seed_patient(db_session, name="Eve", rut="10.000.000-5")
    await seed_patient(db_session, name="Mallory", rut="10.000.000-6")

    # page=2, size=2 -> debe traer 2
    r = await async_client.get(f"{BASE}/", params={"page": 2, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["page"] == 2
    assert body["meta"]["page_size"] == 2
    assert body["meta"]["total_items"] == 6
    assert body["meta"]["total_pages"] == 3
    assert len(body["items"]) == 2

    # search por nombre
    r2 = await async_client.get(f"{BASE}/", params={"search": "Mall"})
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert any(p["name"] == "Mallory" for p in items)


# ---------------
# GET BY ID (200/404)
# ---------------
@pytest.mark.asyncio
async def test_get_patient_200(
    async_client, auth_user_manager_safe, doctor_user, db_session: AsyncSession
):
    auth_user_manager_safe(doctor_user)
    p = await seed_patient(db_session, name="Zoe", rut="99.999.999-9")
    r = await async_client.get(f"{BASE}/{p.id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Zoe"


@pytest.mark.asyncio
async def test_get_patient_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user)
    r = await async_client.get(f"{BASE}/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Patient not found"


# ---------------
# UPDATE (200/404/409)
# ---------------
@pytest.mark.asyncio
async def test_update_patient_200(
    async_client, auth_user_manager_safe, doctor_user, db_session: AsyncSession
):
    auth_user_manager_safe(doctor_user, is_doctor=True)  # require_medical_role
    p = await seed_patient(db_session, name="Old", rut="33.333.333-3")
    r = await async_client.patch(f"{BASE}/{p.id}", json={"name": "New Name"})
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_patient_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    r = await async_client.patch(f"{BASE}/123456", json={"name": "X"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Patient not found"


@pytest.mark.asyncio
async def test_update_patient_conflict_rut_409(
    async_client, auth_user_manager_safe, doctor_user, db_session: AsyncSession
):
    auth_user_manager_safe(doctor_user, is_doctor=True)

    # p1 = await seed_patient(db_session, name="A1", rut="44.444.444-4")
    await seed_patient(db_session, name="A1", rut="44.444.444-4")
    p2 = await seed_patient(db_session, name="A2", rut="55.555.555-5")
    # intentar cambiar el rut de p2 al de p1
    r = await async_client.patch(f"{BASE}/{p2.id}", json={"rut": "44.444.444-4"})
    assert r.status_code == 409
    assert r.json()["detail"] == "RUT ya registrado"


@pytest.mark.asyncio
async def test_delete_patient_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_admin=True)
    r = await async_client.delete(f"{BASE}/404")
    assert r.status_code == 404
    assert r.json()["detail"] == "Patient not found"


@pytest.mark.asyncio
async def test_list_patient_episodes_404_patient_not_found(
    async_client, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user)
    r = await async_client.get(f"{BASE}/999999/episodes")
    assert r.status_code == 404
    assert r.json()["detail"] == "Patient not found"


@pytest.mark.asyncio
async def test_list_patient_episodes_empty(
    async_client, auth_user_manager_safe, doctor_user, make_patient_isolated
):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    pid = await make_patient_isolated()
    res = await async_client.get(f"{BASE}/{pid}/episodes")
    # debe devolver lista vacía, no error
    assert res.status_code == 200
    assert isinstance(res.json(), list)
