import pytest

from club777_api.auth.security import hash_password
from club777_api.auth.service import (
    InvalidRefreshTokenError,
    issue_tokens,
    rotate_refresh_token,
)
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
        password_hash=hash_password("correcta123"),
        full_name="Ana Pérez",
        role="cajero",
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_issue_tokens_creates_access_and_refresh_token(db_session):
    user = _create_user(db_session)

    access_token, refresh_token = issue_tokens(db_session, user)

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)
    assert access_token != refresh_token


def test_rotate_refresh_token_succeeds_with_valid_token(db_session):
    user = _create_user(db_session)
    _, refresh_token = issue_tokens(db_session, user)

    new_access_token, new_refresh_token = rotate_refresh_token(
        db_session, refresh_token
    )

    assert isinstance(new_access_token, str)
    assert new_refresh_token != refresh_token


def test_rotate_refresh_token_rejects_unknown_token(db_session):
    _create_user(db_session)

    with pytest.raises(InvalidRefreshTokenError):
        rotate_refresh_token(db_session, "token_que_nunca_existio")


def test_reused_refresh_token_revokes_entire_family(db_session):
    user = _create_user(db_session)
    _, original_refresh_token = issue_tokens(db_session, user)

    # Uso normal: Ana rota su token a las 8:15am, como en la historia.
    new_access_token, rotated_refresh_token = rotate_refresh_token(
        db_session, original_refresh_token
    )

    # El atacante intenta usar el token viejo, ya revocado (interceptado antes).
    with pytest.raises(InvalidRefreshTokenError):
        rotate_refresh_token(db_session, original_refresh_token)

    # Consecuencia esperada: el token vigente de Ana (el rotado) también
    # queda revocado, aunque ella no hizo nada malo.
    with pytest.raises(InvalidRefreshTokenError):
        rotate_refresh_token(db_session, rotated_refresh_token)
