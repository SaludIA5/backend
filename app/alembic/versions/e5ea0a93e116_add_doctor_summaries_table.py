"""add doctor_summaries table

Revision ID: e5ea0a93e116
Revises: cd72594da8af
Create Date: 2025-11-25 01:46:48.234075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e5ea0a93e116'
down_revision: Union[str, Sequence[str], None] = 'cd72594da8af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create doctor_summaries table."""
    op.create_table(
        "doctor_summaries",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("episode_id", sa.Integer(), sa.ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("comment", sa.Text(), nullable=False),
        # si usas created_at/updated_at en todas tus tablas:
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("doctor_summaries")
