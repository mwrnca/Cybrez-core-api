"""add personas

Revision ID: f08aa70f4750
Revises: 4261486862e5
Create Date: 2026-08-16 19:57:39.808846

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f08aa70f4750"
down_revision: Union[str, Sequence[str], None] = "4261486862e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "personas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("public_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("is_directory_visible", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_personas_id"),
        "personas",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_personas_is_directory_visible"),
        "personas",
        ["is_directory_visible"],
        unique=False,
    )

    op.create_index(
        op.f("ix_personas_is_public"),
        "personas",
        ["is_public"],
        unique=False,
    )

    op.create_index(
        op.f("ix_personas_public_id"),
        "personas",
        ["public_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_personas_slug"),
        "personas",
        ["slug"],
        unique=True,
    )

    op.create_index(
        op.f("ix_personas_type"),
        "personas",
        ["type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_personas_user_id"),
        "personas",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_personas_user_id"),
        table_name="personas",
    )

    op.drop_index(
        op.f("ix_personas_type"),
        table_name="personas",
    )

    op.drop_index(
        op.f("ix_personas_slug"),
        table_name="personas",
    )

    op.drop_index(
        op.f("ix_personas_public_id"),
        table_name="personas",
    )

    op.drop_index(
        op.f("ix_personas_is_public"),
        table_name="personas",
    )

    op.drop_index(
        op.f("ix_personas_is_directory_visible"),
        table_name="personas",
    )

    op.drop_index(
        op.f("ix_personas_id"),
        table_name="personas",
    )

    op.drop_table("personas")