from datetime import UTC, datetime, timedelta

import jwt

from club777_api.core.config import settings
from club777_api.users.models import User


def create_access_token(user: User) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": str(user.id),
        "org_id": str(user.org_id),
        "role": user.role,
        "exp": expire,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
