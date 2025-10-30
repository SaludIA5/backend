from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Episode
from app.repositories.episode import EpisodeRepository

BASE = "/episodes"


# -------------------------------
# Helpers: crear episodios via API
# -------------------------------
@pytest.mark.asyncio
async def test_list_episodes_filter_by_patient(
    async_client,
    auth_user_manager_safe,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
):
    """GET /episodes con filtro patient_id y paginación."""
    auth_user_manager_safe(doctor_user, is_doctor=True)

    # 2 pacientes con episodios distintos
    p1 = await make_patient_isolated()
    p2 = await make_patient_isolated()

    # p1 -> 3 episodios, p2 -> 2 episodios
    eids_p1 = [await make_episode_isolated(p1) for _ in range(3)]
    eids_p2 = [await make_episode_isolated(p2) for _ in range(2)]

    # Filtrar por p1
    r = await async_client.get(
        f"{BASE}/", params={"patient_id": p1, "page": 1, "page_size": 10}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total_items"] == 3
    assert len(body["items"]) == 3
    got_ids = {e["id"] for e in body["items"]}
    assert got_ids == set(eids_p1)

    # Filtrar por p2
    r2 = await async_client.get(
        f"{BASE}/", params={"patient_id": p2, "page": 1, "page_size": 10}
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["meta"]["total_items"] == 2
    assert len(body2["items"]) == 2
    assert {e["id"] for e in body2["items"]} == set(eids_p2)


@pytest.mark.asyncio
async def test_get_patient_episodes_groups_open_closed(
    async_client,
    auth_user_manager_safe,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
):
    """GET /episodes/status/{patient_id} agrupa open_episodes y closed_episodes por estado_del_caso."""
    auth_user_manager_safe(doctor_user, is_doctor=True)
    patient_id = await make_patient_isolated()

    # Crea 2 episodios abiertos
    e_open1 = await make_episode_isolated(patient_id)
    e_open2 = await make_episode_isolated(patient_id)

    # Cierra uno vía PATCH (estado_del_caso = 'Cerrado')
    r_patch = await async_client.patch(
        f"{BASE}/{e_open2}", json={"estado_del_caso": "Cerrado"}
    )
    assert r_patch.status_code == 200

    # Consulta status
    r = await async_client.get(f"{BASE}/status/{patient_id}")
    assert r.status_code == 200
    body = r.json()
    open_ids = {e["id"] for e in body["open_episodes"]}
    closed_ids = {e["id"] for e in body["closed_episodes"]}
    assert e_open1 in open_ids
    assert e_open2 in closed_ids


@pytest.mark.asyncio
async def test_get_patient_episodes_404(
    async_client, auth_user_manager_safe, doctor_user
):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    r = await async_client.get(f"{BASE}/status/999999")  # sin episodios
    assert r.status_code == 404
    assert r.json()["detail"] == "No episodes found for this patient"


@pytest.mark.asyncio
async def test_update_episode_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    r = await async_client.patch(f"{BASE}/123456789", json={"tipo": "URGENTE"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Episode not found"


@pytest.mark.asyncio
async def test_update_episode_409_duplicate_numero(
    async_client,
    auth_user_manager_safe,
    doctor_user,
    make_patient_isolated,
    make_episode_isolated,
):
    """Intentar cambiar numero_episodio a uno existente -> 409."""
    auth_user_manager_safe(doctor_user, is_doctor=True)
    p = await make_patient_isolated()
    e1 = await make_episode_isolated(p)
    e2 = await make_episode_isolated(p)

    # Obtiene detalle de e1 para leer "numero_episodio"
    g = await async_client.get(f"{BASE}/{e1}")
    assert g.status_code == 200
    numero_dup = g.json()["numero_episodio"]

    # Actualiza e2 con el numero de e1 -> debe chocar unique
    r = await async_client.patch(f"{BASE}/{e2}", json={"numero_episodio": numero_dup})
    assert r.status_code == 409
    assert r.json()["detail"] == "numero_episodio ya registrado"


@pytest.mark.asyncio
async def test_delete_episode_404(async_client, auth_user_manager_safe, doctor_user):
    auth_user_manager_safe(doctor_user, is_admin=True)
    r = await async_client.delete(f"{BASE}/404")
    assert r.status_code == 404
    assert r.json()["detail"] == "Episode not found"


@pytest.mark.asyncio
async def test_chief_validate_episode_conflict(
    async_client,
    auth_user_manager_safe,
    chief_user,
    make_patient_isolated,
    make_episode_isolated,
):
    auth_user_manager_safe(chief_user, is_chief_doctor=True)
    pid = await make_patient_isolated()
    eid = await make_episode_isolated(pid)
    # primero sin validación previa
    res = await async_client.post(
        f"{BASE}/{eid}/chief-validate",
        json={"user_id": chief_user.id, "decision": "PERTINENTE"},
    )
    assert res.status_code in (400, 409)
