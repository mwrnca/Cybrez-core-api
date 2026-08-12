"""convert organization and membership foreign keys to UUID

Revision ID: dd58c3936e84
Revises: 0695e719334e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "dd58c3936e84"
down_revision: Union[str, Sequence[str], None] = "0695e719334e"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # Drop existing foreign keys first
    op.drop_constraint(
        "memberships_user_id_fkey",
        "memberships",
        type_="foreignkey",
    )

    op.drop_constraint(
        "memberships_organization_id_fkey",
        "memberships",
        type_="foreignkey",
    )

    op.drop_constraint(
        "organizations_owner_id_fkey",
        "organizations",
        type_="foreignkey",
    )

    # Add temporary UUID columns
    op.add_column(
        "memberships",
        sa.Column(
            "organization_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "memberships",
        sa.Column(
            "user_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "organizations",
        sa.Column(
            "owner_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    # Convert existing integer relationships to UUID relationships
    op.execute("""
        UPDATE memberships m
        SET organization_uuid = o.public_id
        FROM organizations o
        WHERE m.organization_id = o.id
    """)

    op.execute("""
        UPDATE memberships m
        SET user_uuid = u.public_id
        FROM users u
        WHERE m.user_id = u.id
    """)

    op.execute("""
        UPDATE organizations o
        SET owner_uuid = u.public_id
        FROM users u
        WHERE o.owner_id = u.id
    """)

    # Remove old integer columns
    op.drop_column("memberships", "organization_id")
    op.drop_column("memberships", "user_id")
    op.drop_column("organizations", "owner_id")

    # Rename UUID columns
    op.alter_column(
        "memberships",
        "organization_uuid",
        new_column_name="organization_id",
    )

    op.alter_column(
        "memberships",
        "user_uuid",
        new_column_name="user_id",
    )

    op.alter_column(
        "organizations",
        "owner_uuid",
        new_column_name="owner_id",
    )

    # Make them non-null
    op.alter_column(
        "memberships",
        "organization_id",
        nullable=False,
    )

    op.alter_column(
        "memberships",
        "user_id",
        nullable=False,
    )

    op.alter_column(
        "organizations",
        "owner_id",
        nullable=False,
    )

    # Recreate foreign keys
    op.create_foreign_key(
        "memberships_user_id_fkey",
        "memberships",
        "users",
        ["user_id"],
        ["public_id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "memberships_organization_id_fkey",
        "memberships",
        "organizations",
        ["organization_id"],
        ["public_id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "organizations_owner_id_fkey",
        "organizations",
        "users",
        ["owner_id"],
        ["public_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:

    # Drop UUID foreign keys
    op.drop_constraint(
        "memberships_user_id_fkey",
        "memberships",
        type_="foreignkey",
    )

    op.drop_constraint(
        "memberships_organization_id_fkey",
        "memberships",
        type_="foreignkey",
    )

    op.drop_constraint(
        "organizations_owner_id_fkey",
        "organizations",
        type_="foreignkey",
    )

    # Temporary integer columns
    op.add_column(
        "memberships",
        sa.Column(
            "organization_int",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "memberships",
        sa.Column(
            "user_int",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "organizations",
        sa.Column(
            "owner_int",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Convert UUID relationships back to integer IDs
    op.execute("""
        UPDATE memberships m
        SET organization_int = o.id
        FROM organizations o
        WHERE m.organization_id = o.public_id
    """)

    op.execute("""
        UPDATE memberships m
        SET user_int = u.id
        FROM users u
        WHERE m.user_id = u.public_id
    """)

    op.execute("""
        UPDATE organizations o
        SET owner_int = u.id
        FROM users u
        WHERE o.owner_id = u.public_id
    """)

    op.drop_column("memberships", "organization_id")
    op.drop_column("memberships", "user_id")
    op.drop_column("organizations", "owner_id")

    op.alter_column(
        "memberships",
        "organization_int",
        new_column_name="organization_id",
    )

    op.alter_column(
        "memberships",
        "user_int",
        new_column_name="user_id",
    )

    op.alter_column(
        "organizations",
        "owner_int",
        new_column_name="owner_id",
    )

    op.alter_column(
        "memberships",
        "organization_id",
        nullable=False,
    )

    op.alter_column(
        "memberships",
        "user_id",
        nullable=False,
    )

    op.alter_column(
        "organizations",
        "owner_id",
        nullable=False,
    )

    # Restore integer foreign keys
    op.create_foreign_key(
        "memberships_user_id_fkey",
        "memberships",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "memberships_organization_id_fkey",
        "memberships",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "organizations_owner_id_fkey",
        "organizations",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )