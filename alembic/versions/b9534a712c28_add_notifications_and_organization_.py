"""add notifications and organization changes (recovered stub)

Revision ID: b9534a712c28
Revises: dd58c3936e84
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9534a712c28"
down_revision: Union[str, Sequence[str], None] = "dd58c3936e84"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Original migration file was lost. Changes were already applied
    # to the database (confirmed via alembic_version table), so this
    # is an intentional no-op stub to restore the migration chain.
    pass


def downgrade() -> None:
    pass