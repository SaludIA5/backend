"""create model_versions table

Revision ID: 04d4fde71b24
Revises: 7792bf76040c
Create Date: 2025-11-13 11:27:11.390991

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "04d4fde71b24"
down_revision: Union[str, Sequence[str], None] = "7792bf76040c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column(
            "version", sa.String(length=50), nullable=False, unique=True, index=True
        ),
        sa.Column("metric", sa.String(length=50), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("trained_at", sa.Date(), nullable=False),
        sa.Column(
            "active", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("model_versions")
