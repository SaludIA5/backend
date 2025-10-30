from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgresql.models import Episode
from app.services import prediction_service

BASE = "/predictions"


# ---------------------------
# Helpers
# ---------------------------
async def seed_episode(db: AsyncSession, numero="EPI-001"):
    ep = Episode(numero_episodio=numero, tipo="SIN ALERTA", triage=3)
    db.add(ep)
    await db.commit()
    await db.refresh(ep)
    return ep


def fake_prediction(label="PERTINENTE", prob=0.82, model="random_forest"):
    """Resultado falso de predicción"""
    return {
        "prediction": 1 if label == "PERTINENTE" else 0,
        "probability": prob,
        "label": label,
        "model": model,
    }


# ---------------------------
# TESTS
# ---------------------------


@pytest.mark.asyncio
async def test_predict_success_random_forest(
    async_client: AsyncClient, auth_user_manager_safe, doctor_user
):
    """Predicción exitosa con modelo random_forest"""
    auth_user_manager_safe(doctor_user, is_doctor=True)

    payload = {
        "model_type": "random_forest",
        "tipo": "SIN ALERTA",
        "triage": 3,
        "presion_sistolica": 120,
        "presion_diastolica": 80,
        "temperatura_c": 36.5,
    }

    with patch.object(
        prediction_service.PredictionService,
        "predict_episode_pertinence",
        return_value=fake_prediction(),
    ):
        r = await async_client.post(f"{BASE}/", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["label"] in ["PERTINENTE", "NO PERTINENTE"]
        assert 0.0 <= data["probability"] <= 1.0
        assert "update_episode" in data
        assert "model" in data


@pytest.mark.asyncio
async def test_predict_with_invalid_model_type(
    async_client: AsyncClient, auth_user_manager_safe, doctor_user
):
    """Debe devolver 400 por modelo inválido (ValueError en PredictionService)"""
    auth_user_manager_safe(doctor_user, is_doctor=True)

    payload = {"model_type": "invalid_model", "triage": 3}

    with patch.object(
        prediction_service.PredictionService,
        "predict_episode_pertinence",
        side_effect=ValueError("Modelo no soportado"),
    ):
        r = await async_client.post(f"{BASE}/", json=payload)
        assert r.status_code == 400
        assert "Modelo no soportado" in r.json()["detail"]


@pytest.mark.asyncio
async def test_predict_episode_not_found(
    async_client: AsyncClient,
    auth_user_manager_safe,
    doctor_user,
    db_session: AsyncSession,
):
    """Si el episodio no existe, no debe fallar, devuelve mensaje."""
    auth_user_manager_safe(doctor_user, is_doctor=True)
    mock_result = fake_prediction(label="PERTINENTE")

    with patch.object(
        prediction_service.PredictionService,
        "predict_episode_pertinence",
        return_value=mock_result,
    ):
        r = await async_client.post(
            f"{BASE}/",
            json={
                "model_type": "random_forest",
                "id_episodio": 9999,
                "tipo": "SIN ALERTA",
                "triage": 3,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "not found" in data["update_episode"]


@pytest.mark.asyncio
async def test_predict_internal_exception(
    async_client: AsyncClient, auth_user_manager_safe, doctor_user
):
    """Error inesperado en PredictionService -> 500"""
    auth_user_manager_safe(doctor_user, is_doctor=True)

    with patch.object(
        prediction_service.PredictionService,
        "predict_episode_pertinence",
        side_effect=Exception("Exploded!"),
    ):
        r = await async_client.post(f"{BASE}/", json={"model_type": "random_forest"})
        assert r.status_code == 500
        assert "Error al realizar la predicción" in r.json()["detail"]
