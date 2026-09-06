from sqlalchemy.orm import Session

from club777_api.auth.security import verify_password
from club777_api.core.config import settings
from club777_api.users.models import User
from club777_api.users.repository import UserRepository

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
