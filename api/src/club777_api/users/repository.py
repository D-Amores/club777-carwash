from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from club777_api.users.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_by_email(self, org_id: UUID, email: str) -> User | None:
        statement = select(User).where(
            User.org_id == org_id, User.email == email, User.is_active.is_(True)
        )

        return self._session.execute(statement).scalar_one_or_none()
