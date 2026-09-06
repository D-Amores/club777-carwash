from datetime import datetime, timedelta, timezone
from uuid import UUID

from club777_api.organizations.models import Organization
from club777_api.users.models import RefreshToken, User


def test_create_refresh_token_for_user(db_session):
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

    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash="fake_hashed_token_value",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(refresh_token)
    db_session.flush()

    assert isinstance(refresh_token.id, UUID)
    assert refresh_token.id.version == 7
    assert refresh_token.user_id == user.id
    assert refresh_token.revoked_at is None
    assert isinstance(refresh_token.family_id, UUID)
