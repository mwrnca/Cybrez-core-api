"""fix invitation organization uuid and indexes

Revision ID: 946455556da2
Revises: f08aa70f4750
Create Date: 2026-08-16 21:25:43.758326

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "946455556da2"
down_revision: Union[str, Sequence[str], None] = "f08aa70f4750"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the old FK that points to organizations.id.
    op.drop_constraint(
        "invitations_organization_id_fkey",
        "invitations",
        type_="foreignkey",
    )

    # Temporary UUID column used to safely migrate existing integer IDs
    # to the corresponding organization's public_id.
    op.add_column(
        "invitations",
        sa.Column(
            "organization_public_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # Convert existing organization IDs:
    # invitations.organization_id (integer)
    # -> organizations.id
    # -> organizations.public_id (UUID)
    op.execute(
        """
        UPDATE invitations AS i
        SET organization_public_id = o.public_id
        FROM organizations AS o
        WHERE i.organization_id = o.id
        """
    )

    # Remove the old integer column.
    op.drop_column(
        "invitations",
        "organization_id",
    )

    # Rename the UUID column back to organization_id.
    op.alter_column(
        "invitations",
        "organization_public_id",
        new_column_name="organization_id",
        nullable=False,
    )

    # Point the FK at organizations.public_id.
    op.create_foreign_key(
        "invitations_organization_id_fkey",
        "invitations",
        "organizations",
        ["organization_id"],
        ["public_id"],
        ondelete="CASCADE",
    )

    # Indexes required by the current models.
    op.create_index(
        "ix_invitations_organization_id",
        "invitations",
        ["organization_id"],
        unique=False,
    )

    


def downgrade() -> None:
    # Remove indexes added by this migration.
    

    op.drop_index(
        "ix_invitations_organization_id",
        table_name="invitations",
    )

    # Remove the UUID FK.
    op.drop_constraint(
        "invitations_organization_id_fkey",
        "invitations",
        type_="foreignkey",
    )

    # Temporary integer column for converting public_id back to id.
    op.add_column(
        "invitations",
        sa.Column(
            "organization_internal_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Convert:
    # invitations.organization_id (UUID)
    # -> organizations.public_id
    # -> organizations.id (integer)
    op.execute(
        """
        UPDATE invitations AS i
        SET organization_internal_id = o.id
        FROM organizations AS o
        WHERE i.organization_id = o.public_id
        """
    )

    # Remove UUID column.
    op.drop_column(
        "invitations",
        "organization_id",
    )

    # Rename integer column back.
    op.alter_column(
        "invitations",
        "organization_internal_id",
        new_column_name="organization_id",
        nullable=False,
    )

    # Restore original FK.
    op.create_foreign_key(
        "invitations_organization_id_fkey",
        "invitations",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )