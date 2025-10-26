"""merge heads

Revision ID: 7792bf76040c
Revises: ebe1bb1db8f8, 6e11cc700077
Create Date: 2025-10-24 16:10:55.124577

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "7792bf76040c"
down_revision: Union[str, Sequence[str], None] = ("ebe1bb1db8f8", "6e11cc700077")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
