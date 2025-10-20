"""create episode_user table

Revision ID: ebe1bb1db8f8
Revises: c01235e067a0
Create Date: 2025-10-19 21:39:31.192204

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ebe1bb1db8f8"
down_revision: Union[str, Sequence[str], None] = "c01235e067a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "episode_user",
        sa.Column("episode_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("episode_id", "user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("episode_user")
