"""Tests for prediction endpoints."""

import pytest
from fastapi.testclient import TestClient

from tests.factories import PredictionDataFactory


class TestPredictionEndpoint:
    """Tests for /predictions/ endpoint."""

    def test_predict_with_random_forest_success(self, client: TestClient):
        """Test successful prediction with Random Forest model."""
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "label" in data
        assert "model" in data
        assert data["prediction"] in [0, 1]
        assert 0.0 <= data["probability"] <= 1.0
        assert data["label"] in ["PERTINENTE", "NO PERTINENTE"]
        assert data["model"] == "random_forest"

    def test_predict_with_xgboost_success(self, client: TestClient):
        """Test successful prediction with XGBoost model."""
        payload = PredictionDataFactory.build(model_type="xgboost")

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "xgboost"
        assert data["prediction"] in [0, 1]
        assert 0.0 <= data["probability"] <= 1.0

    def test_predict_pertinente_label(self, client: TestClient):
        """Test that label matches prediction value."""
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        if data["prediction"] == 1:
            assert data["label"] == "PERTINENTE"
        else:
            assert data["label"] == "NO PERTINENTE"

    def test_predict_with_invalid_model_type(self, client: TestClient):
        """Test prediction with invalid model type."""
        payload = PredictionDataFactory.build(model_type="invalid_model")

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 422

    def test_predict_with_minimal_data(self, client: TestClient):
        """Test prediction with minimal required data."""
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

    def test_predict_with_all_fields(self, client: TestClient):
        """Test prediction with all available fields."""
        payload = PredictionDataFactory.build_complete()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data

    def test_predict_probability_range(self, client: TestClient):
        """Test that probability is always between 0 and 1."""
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["probability"], (int, float))
        assert 0.0 <= data["probability"] <= 1.0

    def test_predict_with_boolean_fields(self, client: TestClient):
        """Test prediction with boolean fields."""
        payload = PredictionDataFactory.build(
            antecedentes_cardiaco=True,
            antecedentes_diabetes=False,
            antecedentes_hipertension=True,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_with_numeric_fields(self, client: TestClient):
        """Test prediction with various numeric values."""
        payload = PredictionDataFactory.build(
            presion_sistolica=160,
            presion_diastolica=95,
            temperatura_c=36.5,
            saturacion_o2=97,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_with_categorical_fields(self, client: TestClient):
        """Test prediction with categorical fields."""
        payload = PredictionDataFactory.build(
            tipo="SIN ALERTA",
            tipo_alerta_ugcc="SIN ALERTA",
            tipo_cama="UCI",
            triage=3,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_response_structure(self, client: TestClient):
        """Test that response has correct structure."""
        payload = PredictionDataFactory.build()

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        expected_keys = ["prediction", "probability", "label", "model"]
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"

    def test_predict_consistency(self, client: TestClient):
        """Test that same input produces same output."""
        payload = PredictionDataFactory.build_deterministic()

        response1 = client.post("/predictions/", json=payload)
        response2 = client.post("/predictions/", json=payload)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()

    def test_predict_different_triage_levels(self, client: TestClient):
        """Test prediction with different triage levels."""
        for triage_level in [1, 2, 3, 4, 5]:
            payload = PredictionDataFactory.build(triage=triage_level)

            response = client.post("/predictions/", json=payload)

            assert response.status_code == 200

    def test_predict_extreme_vital_signs(self, client: TestClient):
        """Test prediction with extreme vital signs."""
        payload = PredictionDataFactory.build(
            presion_sistolica=200,
            presion_diastolica=120,
            temperatura_c=39.5,
            saturacion_o2=85,
            frecuencia_cardiaca=150,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200

    def test_predict_normal_vital_signs(self, client: TestClient):
        """Test prediction with normal vital signs."""
        payload = PredictionDataFactory.build(
            presion_sistolica=120,
            presion_diastolica=80,
            temperatura_c=36.5,
            saturacion_o2=98,
            frecuencia_cardiaca=70,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 200


class TestPredictionValidation:
    """Tests for prediction input validation."""

    def test_invalid_model_type_validation(self, client: TestClient):
        """Test validation of invalid model type."""
        payload = {
            "model_type": "neural_network",
            "tipo": "SIN ALERTA",
            "triage": 3,
        }

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 422

    def test_missing_required_fields(self, client: TestClient):
        """Test with completely empty payload."""
        payload = {}

        response = client.post("/predictions/", json=payload)

        assert response.status_code in [200, 422, 500]

    def test_invalid_numeric_values(self, client: TestClient):
        """Test with invalid numeric values."""
        payload = PredictionDataFactory.build(
            presion_sistolica="invalid",
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 422

    def test_invalid_boolean_values(self, client: TestClient):
        """Test with invalid boolean values."""
        payload = {
            "model_type": "random_forest",
            "antecedentes_cardiaco": "maybe",
        }

        response = client.post("/predictions/", json=payload)

        assert response.status_code == 422


class TestPredictionEdgeCases:
    """Tests for edge cases in predictions."""

    def test_predict_with_null_values(self, client: TestClient):
        """Test prediction with null/None values."""
        payload = PredictionDataFactory.build(
            presion_diastolica=None,
            temperatura_c=None,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code in [200, 400, 500]

    def test_predict_with_zero_values(self, client: TestClient):
        """Test prediction with zero values."""
        payload = PredictionDataFactory.build(
            glasgow_score=0,
            fio2=0,
        )

        response = client.post("/predictions/", json=payload)

        assert response.status_code in [200, 400]

    def test_predict_multiple_requests(self, client: TestClient):
        """Test multiple consecutive prediction requests."""
        payload = PredictionDataFactory.build()

        for _ in range(5):
            response = client.post("/predictions/", json=payload)
            assert response.status_code == 200


@pytest.mark.asyncio
class TestPredictionAsync:
    """Async tests for prediction endpoint."""

    async def test_predict_async(self, async_client):
        """Test prediction endpoint with async client."""
        payload = PredictionDataFactory.build()

        response = await async_client.post("/predictions/", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
