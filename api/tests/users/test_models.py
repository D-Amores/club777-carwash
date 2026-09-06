import pytest
from sqlalchemy.exc import IntegrityError

from club777_api.organizations.models import Organization
from club777_api.users.models import User


def _create_organization(db_session) -> Organization:
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()
    return organization


def test_create_user_with_valid_role(db_session):
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

    assert user.id is not None
    assert user.role == "cajero"
    assert user.commission_pct == 0


def test_rejects_invalid_role(db_session):
    organization = _create_organization(db_session)

    user = User(
        org_id=organization.id,
        email="invalido@club777.com",
        password_hash="fake_hash_for_now",
        full_name="Usuario Inválido",
        role="gerente",
    )
    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.flush()
