from datetime import UTC, datetime, timedelta

from uuid6 import uuid7

from club777_api.organizations.models import Organization
from club777_api.users.models import User
from club777_api.users.repository import RefreshTokenRepository


def _create_user(db_session) -> User:
    organization = Organization(name="Club 777 Car Wash")
    db_session.add(organization)
    db_session.flush()

    user = User(
        org_id=organization.id,
        email="cajero@club777.com",
        password_hash="fake_hash_for_now",
        full_name="Ana Pérez",
        role="cajero",
    )
    db_session.add(user)
    db_session.flush()
    return user


def _expires_in_seven_days() -> datetime:
    return datetime.now(UTC) + timedelta(days=7)


def test_save_and_get_active_by_hash(db_session):
    user = _create_user(db_session)
    repository = RefreshTokenRepository(db_session)

    saved = repository.save(
        user_id=user.id,
        token_hash="hash_del_token_uno",
        family_id=uuid7(),
        expires_at=_expires_in_seven_days(),
    )

    found = repository.get_active_by_hash("hash_del_token_uno")

    assert found is not None
    assert found.id == saved.id
    assert found.revoked_at is None


def test_revoke_makes_token_inactive(db_session):
    user = _create_user(db_session)
    repository = RefreshTokenRepository(db_session)

    token = repository.save(
        user_id=user.id,
        token_hash="hash_del_token_dos",
        family_id=uuid7(),
        expires_at=_expires_in_seven_days(),
    )

    repository.revoke(token)
    found = repository.get_active_by_hash("hash_del_token_dos")

    assert found is None


def test_revoke_family_revokes_all_tokens_in_family(db_session):
    user = _create_user(db_session)
    repository = RefreshTokenRepository(db_session)
    family_id = uuid7()

    repository.save(
        user_id=user.id,
        token_hash="hash_token_original",
        family_id=family_id,
        expires_at=_expires_in_seven_days(),
    )
    repository.save(
        user_id=user.id,
        token_hash="hash_token_rotado",
        family_id=family_id,
        expires_at=_expires_in_seven_days(),
    )

    repository.revoke_family(family_id)

    assert repository.get_active_by_hash("hash_token_original") is None
    assert repository.get_active_by_hash("hash_token_rotado") is None
