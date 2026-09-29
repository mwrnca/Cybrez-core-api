"""merge refresh sessions and organization units

Revision ID: cb02a172084a
Revises: c2f8b1d6a904, 2b5a1540d10c
Create Date: 2026-09-24 09:22:01.583848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb02a172084a'
down_revision: Union[str, Sequence[str], None] = ('c2f8b1d6a904', '2b5a1540d10c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
