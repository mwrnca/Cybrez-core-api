"""convert project organization_id to uuid

Revision ID: bca07da8545a
Revises: b9534a712c28
Create Date: 2026-08-13 00:27:57.012480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bca07da8545a'
down_revision: Union[str, Sequence[str], None] = 'b9534a712c28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
