import json
from typing import Any, Dict


def assert_response_success(response, expected_status: int = 200):
    """Verificar que una respuesta HTTP sea exitosa."""
    assert response.status_code == expected_status


def assert_response_error(response, expected_status: int = 400):
    """Verificar que una respuesta HTTP sea un error."""
    assert response.status_code == expected_status


def assert_json_response(response, expected_data: Dict[str, Any]):
    """Verificar que una respuesta JSON contenga los datos esperados."""
    data = response.json()
    for key, value in expected_data.items():
        assert data.get(key) == value


def load_test_data(filename: str) -> Dict[str, Any]:
    """Cargar datos de prueba desde un archivo JSON."""
    with open(f"tests/fixtures/{filename}", "r") as f:
        return json.load(f)


def create_test_user_data() -> Dict[str, str]:
    """Crear datos de usuario de prueba."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }
