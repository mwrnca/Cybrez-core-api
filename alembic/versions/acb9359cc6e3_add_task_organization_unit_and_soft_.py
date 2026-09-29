"""add task organization unit and soft delete owner

Revision ID: acb9359cc6e3
Revises: cb02a172084a
Create Date: 2026-09-27 22:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "acb9359cc6e3"
down_revision: Union[str, Sequence[str], None] = "cb02a172084a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organization_units",
        sa.Column(
            "deleted_by",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_organization_units_deleted_by_users",
        "organization_units",
        "users",
        ["deleted_by"],
        ["id"],
    )

    op.add_column(
        "tasks",
        sa.Column(
            "organization_unit_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_tasks_organization_unit_id",
        "tasks",
        "organization_units",
        ["organization_unit_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_tasks_organization_unit_id",
        "tasks",
        ["organization_unit_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tasks_organization_unit_id",
        table_name="tasks",
    )

    op.drop_constraint(
        "fk_tasks_organization_unit_id",
        "tasks",
        type_="foreignkey",
    )

    op.drop_column(
        "tasks",
        "organization_unit_id",
    )

    op.drop_constraint(
        "fk_organization_units_deleted_by_users",
        "organization_units",
        type_="foreignkey",
    )

    op.drop_column(
        "organization_units",
        "deleted_by",
    )