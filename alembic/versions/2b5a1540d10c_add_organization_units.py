"""add organization units

Revision ID: 2b5a1540d10c
Revises: 7c7b39fea624
Create Date: 2026-09-23 14:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "2b5a1540d10c"
down_revision: Union[str, Sequence[str], None] = "7c7b39fea624"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organization_units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "public_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "parent_unit_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.public_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_unit_id"],
            ["organization_units.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id"),
    )

    op.create_index(
        "ix_organization_units_id",
        "organization_units",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_organization_units_public_id",
        "organization_units",
        ["public_id"],
        unique=False,
    )

    op.create_index(
        "ix_organization_units_organization_id",
        "organization_units",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_organization_units_parent_unit_id",
        "organization_units",
        ["parent_unit_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_units_parent_unit_id",
        table_name="organization_units",
    )
    op.drop_index(
        "ix_organization_units_organization_id",
        table_name="organization_units",
    )
    op.drop_index(
        "ix_organization_units_public_id",
        table_name="organization_units",
    )
    op.drop_index(
        "ix_organization_units_id",
        table_name="organization_units",
    )
    op.drop_table("organization_units")