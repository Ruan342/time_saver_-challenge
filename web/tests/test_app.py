import os
import sys
import tempfile
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("SECRET_KEY", "test-secret")


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    os.environ["DATABASE_PATH"] = db_path
    os.environ["TEST_USER_EMAIL"] = "teste@timesaver.com"
    os.environ["TEST_USER_PASSWORD"] = "teste123"

    import db
    import seed

    db.init_db()
    seed.seed_test_user()

    import app as app_module

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client

    os.close(db_fd)
    os.unlink(db_path)


def test_login_valido(client):
    response = client.post(
        "/login",
        data={"identifier": "teste@timesaver.com", "password": "teste123"},
    )
    assert response.status_code == 302
    assert "/agenda" in response.headers["Location"]


def test_login_invalido(client):
    response = client.post(
        "/login",
        data={"identifier": "teste@timesaver.com", "password": "senha-errada"},
    )
    assert response.status_code == 200
    assert "inválidos" in response.get_data(as_text=True)


def test_busca_sem_resultado(client):
    client.post(
        "/login",
        data={"identifier": "teste@timesaver.com", "password": "teste123"},
    )

    mock_data = [
        {
            "paciente": "Maria Silva",
            "cpf": "123.456.789-00",
            "medico": "Dr. João",
            "especialidade": "Cardiologia",
            "data": "2026-07-21",
            "horario": "09:00",
            "convenio": "Unimed",
            "status": "Confirmado",
        }
    ]

    with patch("app.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json = lambda: mock_data

        response = client.get("/api/agendamentos?q=paciente-inexistente")
        assert response.status_code == 200
        assert response.get_json() == []


def test_api_indisponivel(client):
    client.post(
        "/login",
        data={"identifier": "teste@timesaver.com", "password": "teste123"},
    )

    import requests as requests_module

    with patch("app.requests.get", side_effect=requests_module.exceptions.ConnectionError()):
        response = client.get("/api/agendamentos")
        assert response.status_code == 503
        assert "error" in response.get_json()
