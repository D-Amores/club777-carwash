from uuid import UUID

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from club777_api.core.models import Base, TimestampMixin


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(
        String, nullable=False, default="America/Mexico_City"
    )
    currency: Mapped[str] = mapped_column(String, nullable=False, default="MXN")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
