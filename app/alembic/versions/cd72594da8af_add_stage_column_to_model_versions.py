"""add stage column to model_versions

Revision ID: cd72594da8af
Revises: 6839f4efda73
Create Date: 2025-11-14 17:45:53.361714

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cd72594da8af"
down_revision: Union[str, Sequence[str], None] = "6839f4efda73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "model_versions",
        sa.Column("stage", sa.String(length=10), nullable=False, server_default="dev"),
    )


def downgrade():
    op.drop_column("model_versions", "stage")
