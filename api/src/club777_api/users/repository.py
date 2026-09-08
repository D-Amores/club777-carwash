from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from club777_api.users.models import RefreshToken, User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_by_email(self, org_id: UUID, email: str) -> User | None:
        statement = select(User).where(
            User.org_id == org_id, User.email == email, User.is_active.is_(True)
        )

        return self._session.execute(statement).scalar_one_or_none()


class RefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self, user_id: UUID, token_hash: str, family_id: UUID, expires_at: datetime
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
        )

        self._session.add(refresh_token)
        self._session.flush()
        return refresh_token

    def get_active_by_hash(self, token_hash: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )

        return self._session.execute(statement).scalar_one_or_none()

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self._session.execute(statement).scalar_one_or_none()

    def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(UTC)
        self._session.flush()

    def revoke_family(self, family_id: UUID) -> None:
        statement = select(RefreshToken).where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )

        tokens = self._session.execute(statement).scalars().all()

        for token in tokens:
            token.revoked_at = datetime.now(UTC)

        self._session.flush()
