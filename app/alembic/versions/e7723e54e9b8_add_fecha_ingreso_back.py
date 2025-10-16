"""add_fecha_ingreso_back

Revision ID: e7723e54e9b8
Revises: 0ae267eab3df
Create Date: 2025-10-15 21:43:39.389973

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7723e54e9b8"
# down_revision: Union[str, Sequence[str], None] = '0ae267eab3df'
down_revision: Union[str, Sequence[str], None] = "4d97e8a97167"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("episodes", sa.Column("fecha_ingreso", sa.Date(), nullable=True))
    op.add_column("episodes", sa.Column("pcr", sa.Numeric(6, 2), nullable=True))


def downgrade():
    op.drop_column("episodes", "pcr")
    op.drop_column("episodes", "fecha_ingreso")
