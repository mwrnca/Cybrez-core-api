import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import SoftDeleteMixin


class OrganizationUnit(SoftDeleteMixin, Base):
    __tablename__ = "organization_units"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.public_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_unit_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("organization_units.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    organization = relationship(
        "Organization",
        back_populates="organization_units",
    )

    parent = relationship(
        "OrganizationUnit",
        remote_side=[id],
        back_populates="children",
    )

    children = relationship(
        "OrganizationUnit",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    @property
    def organization_public_id(self):
        return self.organization.public_id