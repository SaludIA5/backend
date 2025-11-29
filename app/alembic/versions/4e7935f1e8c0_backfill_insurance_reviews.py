"""Backfill insurance reviews for existing episodes

Revision ID: 4e7935f1e8c0
Revises: 8791bf230a1c
Create Date: 2025-11-25 12:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4e7935f1e8c0"
down_revision: Union[str, Sequence[str], None] = "8791bf230a1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO insurance_reviews (episode_id, is_pertinent)
            SELECT e.id, false
            FROM episodes AS e
            WHERE NOT EXISTS (
                SELECT 1
                FROM insurance_reviews AS ir
                WHERE ir.episode_id = e.id
            )
            """
        )
    )


def downgrade() -> None:
    raise RuntimeError(
        "Downgrade not supported: removing historical insurance_reviews rows is unsafe."
    )
