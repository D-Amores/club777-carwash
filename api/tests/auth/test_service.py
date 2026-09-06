from club777_api.auth.security import hash_password
from club777_api.auth.service import authenticate
from club777_api.organizations.models import Organization
from club777_api.users.models import User


def _create_active_user(db_session, org_id, email, password):
    user = User(
        org_id=org_id,
        email=email,
        password_hash=hash_password(password),
        full_name="Usuario de Prueba",
        role="cajero",
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_authenticate_succeeds_with_correct_credentials(db_session, monkeypatch):
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()
    monkeypatch.setattr(
        "club777_api.auth.service.settings.default_org_id", organization.id
    )

    user = _create_active_user(
        db_session, organization.id, "cajero@club777.com", "correcta123"
    )

    result = authenticate(db_session, "cajero@club777.com", "correcta123")

    assert result is not None
    assert result.id == user.id


def test_authenticate_fails_with_wrong_password(db_session, monkeypatch):
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()
    monkeypatch.setattr(
        "club777_api.auth.service.settings.default_org_id", organization.id
    )

    _create_active_user(
        db_session, organization.id, "cajero@club777.com", "correcta123"
    )

    result = authenticate(db_session, "cajero@club777.com", "incorrecta")

    assert result is None


def test_authenticate_fails_when_email_does_not_exist(db_session, monkeypatch):
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()
    monkeypatch.setattr(
        "club777_api.auth.service.settings.default_org_id", organization.id
    )

    result = authenticate(db_session, "no_existe@club777.com", "cualquiera")

    assert result is None
