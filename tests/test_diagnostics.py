import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Diagnostic

BASE = "/diagnostics"


async def seed_diag(db: AsyncSession, code: str, desc: str | None = None) -> Diagnostic:
    d = Diagnostic(cie_code=code, description=desc)
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return d


# LIST (requiere login)
@pytest.mark.asyncio
async def test_list_diagnostics_pagination(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    for i in range(12):
        await seed_diag(db_session, f"X{i:02d}", f"Desc {i}")

    r = await async_client.get(f"{BASE}/", params={"page": 2, "page_size": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["page"] == 2
    assert body["meta"]["page_size"] == 5
    assert body["meta"]["total_items"] == 12
    assert body["meta"]["total_pages"] == 3
    assert len(body["items"]) == 5


@pytest.mark.asyncio
async def test_list_diagnostics_search(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    await seed_diag(db_session, "A00", "Cholera")
    await seed_diag(db_session, "B00", "Herpes")
    await seed_diag(db_session, "C00", "Other")

    r = await async_client.get(f"{BASE}/", params={"search": "her"})
    assert r.status_code == 200
    items = r.json()["items"]
    assert any(it["cie_code"] == "B00" for it in items)


# GET by ID (requiere login)
@pytest.mark.asyncio
async def test_get_diagnostic_200(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    d = await seed_diag(db_session, "B00", "Herpesviral")
    r = await async_client.get(f"{BASE}/{d.id}")
    assert r.status_code == 200
    assert r.json()["cie_code"] == "B00"


@pytest.mark.asyncio
async def test_get_diagnostic_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    r = await async_client.get(f"{BASE}/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Diagnostic not found"


# CREATE (Admin)
@pytest.mark.asyncio
async def test_create_diagnostic_201(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_admin=True)  # simula admin
    payload = {"cie_code": "A00", "description": "Cholera"}
    r = await async_client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["cie_code"] == "A00"


@pytest.mark.asyncio
async def test_create_diagnostic_conflict_409(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_admin=True)
    await seed_diag(db_session, "DUP", "exists")
    r = await async_client.post(
        f"{BASE}/", json={"cie_code": "DUP", "description": "x"}
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "CIE code ya registrado"


# UPDATE (Admin)
@pytest.mark.asyncio
async def test_update_diagnostic_200(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_admin=True)
    d = await seed_diag(db_session, "C00", "Antes")
    r = await async_client.patch(
        f"{BASE}/{d.id}", json={"cie_code": "C01", "description": "Despues"}
    )
    assert r.status_code == 200
    j = r.json()
    assert j["cie_code"] == "C01" and j["description"] == "Despues"
    row = await db_session.get(Diagnostic, d.id)
    assert row.cie_code == "C01"


@pytest.mark.asyncio
async def test_update_diagnostic_conflict_409(
    async_client, db_session: AsyncSession, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_admin=True)
    d2 = await seed_diag(db_session, "D01", "dos")
    r = await async_client.patch(f"{BASE}/{d2.id}", json={"cie_code": "D00"})
    assert r.status_code == 409
    assert r.json()["detail"] == "CIE code ya registrado"


@pytest.mark.asyncio
async def test_update_diagnostic_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_admin=True)
    r = await async_client.patch(f"{BASE}/123456", json={"description": "n/a"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Diagnostic not found"


@pytest.mark.asyncio
async def test_delete_diagnostic_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_admin=True)
    r = await async_client.delete(f"{BASE}/404")
    assert r.status_code == 404
    assert r.json()["detail"] == "Diagnostic not found"
