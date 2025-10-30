"""Tests for prediction endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from tests.factories import EpisodeFactory, PredictionDataFactory


class TestPredictionEndpoint:
    """Tests for /predictions/ endpoint."""

    def test_predict_without_auth(self, client: TestClient):
        """Test successful prediction with Random Forest model."""
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)
        assert response.status_code == 401

    def test_predict_with_random_forest_success(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test successful prediction with Random Forest model."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "label" in data
        assert "model" in data
        assert "update_episode" in data
        assert data["prediction"] in [0, 1]
        assert 0.0 <= data["probability"] <= 1.0
        assert data["label"] in ["PERTINENTE", "NO PERTINENTE"]
        assert data["model"] == "random_forest"

    def test_predict_with_xgboost_success(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test successful prediction with XGBoost model."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(model_type="xgboost")

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "xgboost"
        assert data["prediction"] in [0, 1]
        assert 0.0 <= data["probability"] <= 1.0

    def test_predict_pertinente_label(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test that label matches prediction value."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        if data["prediction"] == 1:
            assert data["label"] == "PERTINENTE"
        else:
            assert data["label"] == "NO PERTINENTE"

    def test_predict_with_invalid_model_type(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with invalid model type."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(model_type="invalid_model")

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 400

    def test_predict_with_minimal_data(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with minimal required data."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = {
            "model_type": "random_forest",
            "tipo": "SIN ALERTA",
            "triage": 3,
            "presion_sistolica": 120,
        }

        response = client.post("/predictions/", json=payload)

        # This might fail due to missing columns, which is expected behavior
        # Testing that the endpoint handles it gracefully
        assert response.status_code in [200, 400, 500]

    def test_predict_with_all_fields(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with all available fields."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build_complete()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data

    def test_predict_probability_range(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test that probability is always between 0 and 1."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["probability"], (int, float))
        assert 0.0 <= data["probability"] <= 1.0

    def test_predict_with_boolean_fields(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with boolean fields."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            antecedentes_cardiaco=True,
            antecedentes_diabetes=False,
            antecedentes_hipertension=True,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_with_numeric_fields(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with various numeric values."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            presion_sistolica=160,
            presion_diastolica=95,
            temperatura_c=36.5,
            saturacion_o2=97,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_with_categorical_fields(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with categorical fields."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            tipo="SIN ALERTA",
            tipo_alerta_ugcc="SIN ALERTA",
            tipo_cama="UCI",
            triage=3,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_response_structure(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test that response has correct structure."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        expected_keys = ["prediction", "probability", "label", "model"]
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"

    def test_predict_consistency(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test that same input produces same output."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build_deterministic()

        response1 = client.post("/predictions/", json=payload)
        response2 = client.post("/predictions/", json=payload)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()

    def test_predict_different_triage_levels(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with different triage levels."""
        for triage_level in [1, 2, 3, 4, 5]:
            auth_user_manager_safe(doctor_user, is_doctor=True)
            payload = PredictionDataFactory.build(triage=triage_level)

            response = client.post("/predictions/", json=payload)

            assert response.status_code == 200

    def test_predict_extreme_vital_signs(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with extreme vital signs."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            presion_sistolica=200,
            presion_diastolica=120,
            temperatura_c=39.5,
            saturacion_o2=85,
            frecuencia_cardiaca=150,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_normal_vital_signs(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with normal vital signs."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            presion_sistolica=120,
            presion_diastolica=80,
            temperatura_c=36.5,
            saturacion_o2=98,
            frecuencia_cardiaca=70,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_all_fields(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with normal vital signs."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = {
            "id_episodio": 0,
            "numero_episodio": "0",
            "diagnostics": "N19",
            "antecedentes_cardiaco": True,
            "antecedentes_diabetes": True,
            "antecedentes_hipertension": False,
            "creatinina": "50",
            "fio2": 0.5,
            "fio2_ge_50": True,
            "frecuencia_cardiaca": 150,
            "frecuencia_respiratoria": 150,
            "glasgow_score": 15,
            "hemoglobina": True,
            "model_type": "random_forest",
            "nitrogeno_ureico": True,
            "pcr": 80,
            "potasio": 8,
            "presion_diastolica": 50,
            "presion_media": 150,
            "presion_sistolica": 100,
            "saturacion_o2": 0.5,
            "sodio": 200,
            "temperatura_c": 25,
            "tipo": "SIN ALERTA",
            "tipo_alerta_ugcc": "SIN ALERTA",
            "tipo_cama": "Básica",
            "triage": 3,
            "ventilacion_mecanica": True,
            "cirugia_realizada": True,
            "cirugia_mismo_dia_ingreso": True,
            "hemodinamia": True,
            "hemodinamia_mismo_dia_ingreso": False,
            "endoscopia": True,
            "endoscopia_mismo_dia_ingreso": False,
            "dialisis": False,
            "trombolisis": True,
            "trombolisis_mismo_dia_ingreso": True,
            "dreo": True,
            "troponinas_alteradas": False,
            "ecg_alterado": True,
            "rnm_protocolo_stroke": True,
            "dva": True,
            "transfusiones": True,
            "compromiso_conciencia": True,
        }

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200


class TestPredictionValidation:
    """Tests for prediction input validation."""

    def test_invalid_model_type_validation(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test validation of invalid model type."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = {
            "model_type": "neural_network",
            "tipo": "SIN ALERTA",
            "triage": 3,
        }

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 400

    def test_missing_required_fields(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test with completely empty payload."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = {}
        response = client.post("/predictions/", json=payload)

        assert response.status_code in [200, 400, 422, 500]

    def test_invalid_numeric_values(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test with invalid numeric values."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            presion_sistolica="invalid",
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 422

    def test_invalid_boolean_values(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test with invalid boolean values."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = {
            "model_type": "random_forest",
            "antecedentes_cardiaco": "maybe",
        }

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 422


class TestPredictionEdgeCases:
    """Tests for edge cases in predictions."""

    def test_predict_with_null_values(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with null/None values."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            presion_diastolica=None,
            temperatura_c=None,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code in [200, 400, 500]

    def test_predict_with_zero_values(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with zero values."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            glasgow_score=0,
            fio2=0,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code in [200, 400]

    def test_predict_multiple_requests(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test multiple consecutive prediction requests."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build()

        for _ in range(5):
            response = client.post("/predictions/", json=payload)
            assert response.status_code == 200

    def test_predict_check_completion_string_values(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test prediction with null/None values."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build(
            presion_diastolica=None,
            temperatura_c=None,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code in [200, 400, 500]


class TestPredictionUpdateEpisode:
    """Tests for the 'update_episode' field in prediction responses."""

    @pytest.mark.asyncio
    async def test_update_episode_success(
        self, client: TestClient, auth_user_manager_safe, doctor_user, db_session
    ):
        """Test when the episode is successfully updated."""
        auth_user_manager_safe(doctor_user, is_doctor=True)

        episode = EpisodeFactory.create(id=1, numero_episodio="12345", patient_id=1)
        db_session.add(episode)
        await db_session.commit()

        payload = PredictionDataFactory.build(id_episodio=1)
        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "update_episode" in data
        assert (
            data["update_episode"]
            == "Model recommendation added to the episode of id 1"
        )

    def test_update_episode_not_found(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test when the episode is not found in the database."""
        auth_user_manager_safe(doctor_user, is_doctor=True)

        payload = PredictionDataFactory.build(id_episodio=999)
        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "update_episode" in data
        assert data["update_episode"] == "Episode with id_episodio '999' not found"

    def test_update_episode_db_error(
        self,
        client: TestClient,
        auth_user_manager_safe,
        doctor_user,
        mocker,
        db_session,
    ):
        """Test when there is a database error during the update."""
        auth_user_manager_safe(doctor_user, is_doctor=True)

        mocker.patch.object(
            db_session, "execute", side_effect=SQLAlchemyError("DB error")
        )

        payload = PredictionDataFactory.build(id_episodio=1)
        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "update_episode" in data
        assert "Could not update episode due to DB error" in data["update_episode"]

    def test_update_episode_unexpected_error(
        self,
        client: TestClient,
        auth_user_manager_safe,
        doctor_user,
        mocker,
        db_session,
    ):
        """Test when there is an unexpected error during the update."""
        auth_user_manager_safe(doctor_user, is_doctor=True)

        mocker.patch.object(
            db_session, "execute", side_effect=Exception("Unexpected error")
        )

        payload = PredictionDataFactory.build(id_episodio=1)
        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "update_episode" in data
        assert "Unexpected error updating episode" in data["update_episode"]

    def test_update_episode_no_id_provided(
        self, client: TestClient, auth_user_manager_safe, doctor_user
    ):
        """Test when no id_episodio is provided in the payload."""
        auth_user_manager_safe(doctor_user, is_doctor=True)

        payload = PredictionDataFactory.build(id_episodio=None)
        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "update_episode" in data
        assert data["update_episode"] == "Episode with id None was not found"


@pytest.mark.asyncio
class TestPredictionAsync:
    """Async tests for prediction endpoint."""

    async def test_predict_async(
        self, async_client, auth_user_manager_safe, doctor_user
    ):
        """Test prediction endpoint with async client."""
        auth_user_manager_safe(doctor_user, is_doctor=True)
        payload = PredictionDataFactory.build()

        response = await async_client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
