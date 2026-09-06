from club777_api.organizations.models import Organization
from club777_api.users.models import User
from club777_api.users.repository import UserRepository


def _create_organization(db_session) -> Organization:
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()
    return organization


def test_get_active_by_email_finds_existing_user(db_session):
    organization = _create_organization(db_session)
    user = User(
        org_id=organization.id,
        email="cajero@club777.com",
        password_hash="fake_hash_for_now",
        full_name="Ana Pérez",
        role="cajero",
    )
    db_session.add(user)
    db_session.flush()

    repository = UserRepository(db_session)
    found = repository.get_active_by_email(
        org_id=organization.id, email="cajero@club777.com"
    )

    assert found is not None
    assert found.id == user.id


def test_get_active_by_email_returns_none_for_inactive_user(db_session):
    organization = _create_organization(db_session)
    user = User(
        org_id=organization.id,
        email="inactivo@club777.com",
        password_hash="fake_hash_for_now",
        full_name="Usuario Desactivado",
        role="cajero",
        is_active=False,
    )
    db_session.add(user)
    db_session.flush()

    repository = UserRepository(db_session)
    found = repository.get_active_by_email(
        org_id=organization.id, email="inactivo@club777.com"
    )

    assert found is None


def test_get_active_by_email_returns_none_for_wrong_organization(db_session):
    organization_a = _create_organization(db_session)
    organization_b = Organization(name="Otro Autolavado")
    db_session.add(organization_b)
    db_session.flush()

    user = User(
        org_id=organization_a.id,
        email="cajero@club777.com",
        password_hash="fake_hash_for_now",
        full_name="Ana Pérez",
        role="cajero",
    )
    db_session.add(user)
    db_session.flush()

    repository = UserRepository(db_session)
    found = repository.get_active_by_email(
        org_id=organization_b.id, email="cajero@club777.com"
    )

    assert found is None
