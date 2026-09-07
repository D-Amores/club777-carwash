from fastapi.testclient import TestClient

from club777_api.auth.security import hash_password
from club777_api.core.database import get_db
from club777_api.main import app
from club777_api.organizations.models import Organization
from club777_api.users.models import User


def _override_get_db(db_session):
    def _get_db():
        yield db_session

    return _get_db


def test_login_succeeds_with_correct_credentials(db_session, monkeypatch):
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()
    monkeypatch.setattr(
        "club777_api.auth.service.settings.default_org_id", organization.id
    )

    user = User(
        org_id=organization.id,
        email="cajero@club777.com",
        password_hash=hash_password("correcta123"),
        full_name="Ana Pérez",
        role="cajero",
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cajero@club777.com", "password": "correcta123"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_fails_with_wrong_password(db_session, monkeypatch):
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()
    monkeypatch.setattr(
        "club777_api.auth.service.settings.default_org_id", organization.id
    )

    user = User(
        org_id=organization.id,
        email="cajero@club777.com",
        password_hash=hash_password("correcta123"),
        full_name="Ana Pérez",
        role="cajero",
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cajero@club777.com", "password": "incorrecta"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas."
