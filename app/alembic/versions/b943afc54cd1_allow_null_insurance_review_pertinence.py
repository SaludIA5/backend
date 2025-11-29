"""Allow null insurance review pertinence values

Revision ID: b943afc54cd1
Revises: 4e7935f1e8c0
Create Date: 2025-11-25 12:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b943afc54cd1"
down_revision: Union[str, Sequence[str], None] = "4e7935f1e8c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "insurance_reviews",
        "is_pertinent",
        existing_type=sa.Boolean(),
        nullable=True,
    )
    op.execute(
        sa.text(
            """
            UPDATE insurance_reviews
            SET is_pertinent = NULL
            WHERE is_pertinent IS FALSE
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE insurance_reviews
            SET is_pertinent = FALSE
            WHERE is_pertinent IS NULL
            """
        )
    )
    op.alter_column(
        "insurance_reviews",
        "is_pertinent",
        existing_type=sa.Boolean(),
        nullable=False,
    )
