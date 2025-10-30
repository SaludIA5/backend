from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import (
    Episode,
    Patient,
    User,
    UserEpisodeValidation,
)

BASE = "/metrics"


async def seed_patient(
    db: AsyncSession, name: str = "John Doe", rut: str = "11.111.111-1", age: int = 40
) -> Patient:
    p = Patient(name=name, rut=rut, age=age)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


async def seed_episode(
    db: AsyncSession,
    *,
    patient_id: int,
    numero_episodio: str,
    recomendacion_modelo: str | None = None,
    validacion: str | None = None,
    validacion_jefe_turno: str | None = None,
    created_at: datetime | None = None,
    validated_by_user: User | int | None = None,
) -> int:
    ep = Episode(
        patient_id=patient_id,
        numero_episodio=numero_episodio,
        tipo="SIN ALERTA",
        triage=3,
        recomendacion_modelo=recomendacion_modelo,
        validacion=validacion,
        validacion_jefe_turno=validacion_jefe_turno,
    )
    if created_at is not None:
        ep.created_at = created_at
    db.add(ep)
    await db.flush()
    episode_id = int(ep.id)
    await db.commit()

    if validated_by_user is not None:
        if isinstance(validated_by_user, int):
            user_id = validated_by_user
        else:
            try:
                insp = sa_inspect(validated_by_user)
                user_id = (
                    insp.identity[0]
                    if insp.identity
                    else getattr(validated_by_user, "id", None)
                )
            except Exception:
                user_id = getattr(validated_by_user, "id", None)

        uev = UserEpisodeValidation(user_id=int(user_id), episode_id=episode_id)
        db.add(uev)
        await db.commit()

    return episode_id


@pytest.mark.asyncio
async def test_metrics_recommendations_empty(
    async_client: "AsyncClient", db_session: AsyncSession
):
    r = await async_client.get(f"{BASE}/recommendations")
    assert r.status_code == 200
    body = r.json()
    assert body["total_recommendations"] == 0
    assert body["accepted_recommendations"] == 0
    assert body["rejected_recommendations"] == 0
    assert body["precision"] == 0.0
    assert body["recall"] == 0.0
    assert body["f1_score"] == 0.0
    assert body["accuracy"] == 0.0


@pytest.mark.asyncio
async def test_metrics_recommendations_confusion_metrics(
    async_client: "AsyncClient",
    db_session: AsyncSession,
    auth_user_manager_safe,
    doctor_user,
):
    auth_user_manager_safe(doctor_user, is_doctor=True)
    p = await seed_patient(db_session, rut="10.000.000-1")
    pid = int(sa_inspect(p).identity[0])

    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="M-001",
        recomendacion_modelo="PERTINENTE",
        validacion="PERTINENTE",
        validated_by_user=doctor_user,
    )
    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="M-002",
        recomendacion_modelo="PERTINENTE",
        validacion="NO PERTINENTE",
        validated_by_user=doctor_user,
    )
    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="M-003",
        recomendacion_modelo="NO PERTINENTE",
        validacion="NO PERTINENTE",
        validated_by_user=doctor_user,
    )
    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="M-004",
        recomendacion_modelo="NO PERTINENTE",
        validacion="PERTINENTE",
        validated_by_user=doctor_user,
    )

    r = await async_client.get(f"{BASE}/recommendations")
    assert r.status_code == 200
    body = r.json()

    assert body["total_recommendations"] == 4
    assert body["accepted_recommendations"] == 4
    assert body["rejected_recommendations"] == 0
    assert body["accepted_concordant"] == 2
    assert body["accepted_discordant"] == 2
    assert pytest.approx(body["precision"], rel=1e-6) == 0.5
    assert pytest.approx(body["recall"], rel=1e-6) == 0.5
    assert pytest.approx(body["f1_score"], rel=1e-6) == 0.5
    assert pytest.approx(body["accuracy"], rel=1e-6) == 0.5
    assert pytest.approx(body["acceptance_rate"], rel=1e-6) == 1.0


@pytest.mark.asyncio
async def test_metrics_validation_by_doctor_groups_and_rates(
    async_client: "AsyncClient",
    db_session: AsyncSession,
    create_user,
    auth_user_manager_safe,
):
    doc_a = await create_user(
        name="Doc A", email="a@ex.com", rut="11111111K", is_doctor=True
    )
    doc_b = await create_user(
        name="Doc B", email="b@ex.com", rut="22222222K", is_doctor=True
    )
    doc_a_id = int(sa_inspect(doc_a).identity[0])
    doc_b_id = int(sa_inspect(doc_b).identity[0])
    auth_user_manager_safe(doc_a, is_doctor=True)
    p = await seed_patient(db_session, rut="10.000.000-2")
    pid = int(sa_inspect(p).identity[0])

    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="V-001",
        recomendacion_modelo="PERTINENTE",
        validacion="PERTINENTE",
        validated_by_user=doc_a,
    )
    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="V-002",
        recomendacion_modelo="NO PERTINENTE",
        validacion="NO PERTINENTE",
        validated_by_user=doc_a,
    )
    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="V-003",
        recomendacion_modelo="PERTINENTE",
        validacion="NO PERTINENTE",
        validated_by_user=doc_a,
    )

    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="V-004",
        recomendacion_modelo="NO PERTINENTE",
        validacion="PERTINENTE",
        validated_by_user=doc_b,
    )

    r = await async_client.get(f"{BASE}/validation-by-doctor")
    assert r.status_code == 200
    rows = r.json()
    row_a = next(x for x in rows if x["doctor_id"] == doc_a_id)
    row_b = next(x for x in rows if x["doctor_id"] == doc_b_id)

    assert row_a["total_validations"] == 3
    assert row_a["concordant_validations"] == 2
    assert row_a["discordant_validations"] == 1
    assert pytest.approx(row_a["concordance_rate"], rel=1e-6) == 2 / 3
    assert pytest.approx(row_a["acceptance_rate"], rel=1e-6) == 1.0

    assert row_b["total_validations"] == 1
    assert row_b["concordant_validations"] == 0
    assert row_b["discordant_validations"] == 1


@pytest.mark.asyncio
async def test_metrics_episodes_pagination_and_fields(
    async_client: "AsyncClient", db_session: AsyncSession, create_user
):
    doc = await create_user(
        name="Doc", email="doc@ex.com", rut="99999999K", is_doctor=True
    )
    p = await seed_patient(db_session, rut="10.000.000-3")
    pid = int(sa_inspect(p).identity[0])

    created_ids = []
    for i in range(6):
        eid = await seed_episode(
            db_session,
            patient_id=pid,
            numero_episodio=f"E-{i}",
            recomendacion_modelo="PERTINENTE" if i % 2 == 0 else "NO PERTINENTE",
            validacion="PERTINENTE" if i % 3 == 0 else None,
            validated_by_user=doc if i < 2 else None,
        )
        created_ids.append(eid)

    r = await async_client.get(f"{BASE}/episodes", params={"limit": 3, "offset": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    sample = items[0]
    assert {
        "episode_id",
        "numero_episodio",
        "patient_id",
        "ai_recommendation",
        "doctor_validation",
        "chief_validation",
        "is_concordant",
        "is_accepted",
        "validation_date",
        "validated_by_doctor",
    }.issubset(set(sample.keys()))


@pytest.mark.asyncio
async def test_metrics_summary_totals(
    async_client: "AsyncClient", db_session: AsyncSession, create_user
):
    doc = await create_user(
        name="Doc S", email="docs@ex.com", rut="99999990K", is_doctor=True
    )
    p = await seed_patient(db_session, rut="10.000.000-4")
    pid = int(sa_inspect(p).identity[0])

    await seed_episode(db_session, patient_id=pid, numero_episodio="S-0")
    _ = await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="S-1",
        recomendacion_modelo="PERTINENTE",
        validacion="PERTINENTE",
        validated_by_user=doc,
    )
    _ = await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="S-2",
        recomendacion_modelo="NO PERTINENTE",
        validacion="NO PERTINENTE",
        validacion_jefe_turno="PERTINENTE",
        validated_by_user=doc,
    )

    r = await async_client.get(f"{BASE}/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["total_episodes"] >= 3
    assert body["episodes_with_ai_recommendation"] >= 2
    assert body["episodes_with_doctor_validation"] >= 2
    assert body["episodes_with_chief_validation"] >= 1
    assert "recommendation_metrics" in body and "validation_metrics" in body


@pytest.mark.asyncio
async def test_metrics_date_filter_recommendations(
    async_client: "AsyncClient", db_session: AsyncSession, create_user
):
    doc = await create_user(
        name="Doc D", email="docd@ex.com", rut="99999992K", is_doctor=True
    )
    p = await seed_patient(db_session, rut="10.000.000-5")
    pid = int(sa_inspect(p).identity[0])

    t0 = datetime.utcnow() - timedelta(days=10)
    t1 = datetime.utcnow() - timedelta(days=5)
    t2 = datetime.utcnow() - timedelta(days=1)

    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="D-0",
        recomendacion_modelo="PERTINENTE",
        validacion="PERTINENTE",
        created_at=t0,
        validated_by_user=doc,
    )
    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="D-1",
        recomendacion_modelo="NO PERTINENTE",
        validacion="NO PERTINENTE",
        created_at=t2,
        validated_by_user=doc,
    )

    r = await async_client.get(
        f"{BASE}/recommendations",
        params={"start_date": (t1.isoformat() + "Z")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total_recommendations"] == 1
    assert body["accepted_recommendations"] == 1


@pytest.mark.asyncio
async def test_metrics_recommendations_no_validations_yields_zero_precision(
    async_client: "AsyncClient", db_session: AsyncSession, create_user
):
    p = await seed_patient(db_session, rut="10.000.000-6")
    pid = int(sa_inspect(p).identity[0])

    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="NV-1",
        recomendacion_modelo="PERTINENTE",
        validacion=None,
    )

    r = await async_client.get(f"{BASE}/recommendations")
    assert r.status_code == 200
    j = r.json()
    assert j["total_recommendations"] >= 1
    assert j["precision"] == 0.0
    assert j["recall"] == 0.0
    assert j["f1_score"] == 0.0
    assert j["accuracy"] == 0.0


@pytest.mark.asyncio
async def test_metrics_end_date_filter_only(
    async_client: "AsyncClient", db_session: AsyncSession, create_user
):
    doc = await create_user(
        name="Doc DT", email="docdt@ex.com", rut="99999994K", is_doctor=True
    )
    p = await seed_patient(db_session, rut="10.000.000-7")
    pid = int(sa_inspect(p).identity[0])

    t_past = datetime.utcnow() - timedelta(days=3)
    t_now = datetime.utcnow()

    await seed_episode(
        db_session,
        patient_id=pid,
        numero_episodio="DF-1",
        recomendacion_modelo="NO PERTINENTE",
        validacion="NO PERTINENTE",
        created_at=t_past,
        validated_by_user=doc,
    )

    r = await async_client.get(
        f"{BASE}/recommendations",
        params={"end_date": (t_now.isoformat() + "Z")},
    )
    assert r.status_code == 200
    assert r.json()["total_recommendations"] >= 1


@pytest.mark.asyncio
async def test_metrics_routes_handle_internal_error(
    async_client: "AsyncClient", monkeypatch
):
    from app.repositories.metric import MetricRepository

    def boom(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(
        MetricRepository, "get_recommendation_metrics", staticmethod(boom)
    )
    r1 = await async_client.get(f"{BASE}/recommendations")
    assert r1.status_code == 500

    monkeypatch.setattr(
        MetricRepository, "get_validation_metrics_by_doctor", staticmethod(boom)
    )
    r2 = await async_client.get(f"{BASE}/validation-by-doctor")
    assert r2.status_code == 500

    monkeypatch.setattr(MetricRepository, "get_episode_metrics", staticmethod(boom))
    r3 = await async_client.get(f"{BASE}/episodes")
    assert r3.status_code == 500

    monkeypatch.setattr(MetricRepository, "get_metrics_summary", staticmethod(boom))
    r4 = await async_client.get(f"{BASE}/summary")
    assert r4.status_code == 500
