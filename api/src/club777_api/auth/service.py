from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session
from uuid6 import uuid7

from club777_api.auth.refresh_tokens import generate_refresh_token, hash_refresh_token
from club777_api.auth.security import verify_password
from club777_api.auth.tokens import create_access_token
from club777_api.core.config import settings
from club777_api.users.models import User
from club777_api.users.repository import RefreshTokenRepository, UserRepository

_DUMMY_HASH = (
    "$argon2id$v=19$m=19456,t=2,p=1$"
    "c29tZXNhbHR2YWx1ZQ$YXJiaXRyYXJ5aGFzaHZhbHVlZm9ydGltaW5n"
)


def authenticate(session: Session, email: str, password: str) -> User | None:
    repository = UserRepository(session)
    user = repository.get_active_by_email(org_id=settings.default_org_id, email=email)

    if user is None:
        verify_password(_DUMMY_HASH, password)
        return None

    if not verify_password(user.password_hash, password):
        return None

    return user


class InvalidRefreshTokenError(Exception):
    pass


def issue_tokens(session: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(user)

    raw_refresh_token = generate_refresh_token()
    RefreshTokenRepository(session).save(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        family_id=uuid7(),
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    return access_token, raw_refresh_token


def rotate_refresh_token(session: Session, raw_refresh_token: str) -> tuple[str, str]:
    repository = RefreshTokenRepository(session)
    token_hash = hash_refresh_token(raw_refresh_token)

    existing = repository.get_by_hash(token_hash)

    if existing is None:
        raise InvalidRefreshTokenError("Refresh token no reconocido.")

    if existing.revoked_at is not None:
        repository.revoke_family(existing.family_id)
        raise InvalidRefreshTokenError(
            "Refresh token reutilizado. Familia revocada por seguridad."
        )

    repository.revoke(existing)

    user = session.get(User, existing.user_id)

    if user is None:
        raise InvalidRefreshTokenError(
            "Usuario asociado al refresh token ya no existe."
        )

    access_token = create_access_token(user)

    raw_new_refresh_token = generate_refresh_token()
    repository.save(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_new_refresh_token),
        family_id=existing.family_id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    return access_token, raw_new_refresh_token
