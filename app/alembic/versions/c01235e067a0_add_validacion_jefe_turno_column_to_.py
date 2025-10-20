"""add validacion_jefe_turno column to Episodes table

Revision ID: c01235e067a0
Revises: ff23329b6cf4
Create Date: 2025-10-19 21:03:56.389244

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c01235e067a0"
down_revision: Union[str, Sequence[str], None] = "ff23329b6cf4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "episodes",
        sa.Column("validacion_jefe_turno", sa.String(length=50), nullable=True),
    )

    print("Iniciando copia de datos de 'validacion' a 'validacion_jefe_turno'...")
    op.execute("UPDATE episodes SET validacion_jefe_turno = validacion")
    print("Copia de datos finalizada.")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("episodes", "validacion_jefe_turno")
