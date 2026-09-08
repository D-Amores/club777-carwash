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


def _setup_user_and_client(db_session, monkeypatch):
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
    return TestClient(app)


def test_login_returns_both_tokens(db_session, monkeypatch):
    client = _setup_user_and_client(db_session, monkeypatch)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cajero@club777.com", "password": "correcta123"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_refresh_returns_new_token_pair(db_session, monkeypatch):
    client = _setup_user_and_client(db_session, monkeypatch)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "cajero@club777.com", "password": "correcta123"},
    )
    original_refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )
    app.dependency_overrides.clear()

    assert refresh_response.status_code == 200
    new_refresh_token = refresh_response.json()["refresh_token"]
    assert new_refresh_token != original_refresh_token


def test_refresh_rejects_unknown_token(db_session, monkeypatch):
    client = _setup_user_and_client(db_session, monkeypatch)

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "token_inventado"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 401


def test_logout_revokes_token_and_subsequent_refresh_fails(db_session, monkeypatch):
    client = _setup_user_and_client(db_session, monkeypatch)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "cajero@club777.com", "password": "correcta123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )

    retry_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    app.dependency_overrides.clear()

    assert logout_response.status_code == 204
    assert retry_response.status_code == 401
