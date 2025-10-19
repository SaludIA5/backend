"""create user_episodes_validations table

Revision ID: 32e0a7b83af2
Revises: ad5fb6362ef3
Create Date: 2025-10-18 18:40:07.092201

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "32e0a7b83af2"
down_revision: Union[str, Sequence[str], None] = "ad5fb6362ef3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_episodes_validations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "episode_id",
            sa.Integer(),
            sa.ForeignKey("episodes.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_episodes_validations")
