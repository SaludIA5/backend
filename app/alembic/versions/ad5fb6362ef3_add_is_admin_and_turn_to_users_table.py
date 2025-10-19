"""Add is_admin and turn to users table

Revision ID: ad5fb6362ef3
Revises: 0ae267eab3df
Create Date: 2025-10-18 16:55:22.620196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ad5fb6362ef3'
down_revision: Union[str, Sequence[str], None] = '0ae267eab3df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('turn', sa.String(length=50), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'turn')
    op.drop_column('users', 'is_admin')