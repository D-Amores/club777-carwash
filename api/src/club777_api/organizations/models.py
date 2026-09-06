from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint, text
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


class Location(Base, TimestampMixin):
    __tablename__ = "locations"
    __table_args__ = (
        UniqueConstraint("org_id", "name", name="ux_locations_org_name"),
        Index("ix_locations_org", "org_id", postgresql_where=text("is_active")),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    org_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str | None] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String)
    timezone: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
